"""
Celery tasks for web crawling.
"""
import hashlib
import logging
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.conf import settings
from django.utils import timezone as django_timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

from .models import CrawlJob, CrawlSource, CrawledContent
from apps.blog.models import Post

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def trigger_crawl_task(self, job_id):
    """
    Main crawl task that processes a crawl job.
    """
    try:
        job = CrawlJob.objects.get(id=job_id)
        source = job.source
        
        # Update job status
        job.status = 'running'
        job.started_at = django_timezone.now()
        job.save()
        
        logger.info(f"Starting crawl job {job_id} for source {source.name}")
        
        # Initialize crawler
        crawler = WebCrawler(job)
        
        # Perform the crawl
        results = crawler.crawl()
        
        # Update job with results
        job.status = 'completed'
        job.completed_at = django_timezone.now()
        job.duration = job.completed_at - job.started_at
        job.pages_crawled = results.get('pages_crawled', 0)
        job.posts_found = results.get('posts_found', 0)
        job.posts_created = results.get('posts_created', 0)
        job.duplicates_found = results.get('duplicates_found', 0)
        job.errors_count = results.get('errors_count', 0)
        job.save()
        
        # Update source statistics
        source.last_crawled_at = django_timezone.now()
        source.total_crawls += 1
        source.successful_crawls += 1
        source.total_posts_found += results.get('posts_found', 0)
        source.save()
        
        logger.info(f"Completed crawl job {job_id} successfully")
        
    except Exception as e:
        logger.error(f"Crawl job {job_id} failed: {str(e)}")
        
        # Update job status
        job = CrawlJob.objects.get(id=job_id)
        job.status = 'failed'
        job.completed_at = django_timezone.now()
        job.error_message = str(e)
        job.save()
        
        # Update source statistics
        source = job.source
        source.total_crawls += 1
        source.failed_crawls += 1
        source.save()
        
        raise


class WebCrawler:
    """
    Web crawler for extracting blog content.
    """
    
    def __init__(self, job):
        self.job = job
        self.source = job.source
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.CRAWL_USER_AGENT
        })
        
        # Results tracking
        self.results = {
            'pages_crawled': 0,
            'posts_found': 0,
            'posts_created': 0,
            'duplicates_found': 0,
            'errors_count': 0
        }
        
        # Visited URLs to avoid duplicates
        self.visited_urls = set()
        
    def crawl(self):
        """
        Main crawl method.
        """
        try:
            # Start crawling from the source URL
            self._crawl_url(self.source.url)
            
            # If follow_links is enabled, crawl additional pages
            if self.source.follow_links and self.results['pages_crawled'] < self.source.max_pages:
                self._crawl_additional_pages()
                
        except Exception as e:
            logger.error(f"Error during crawl: {str(e)}")
            self.results['errors_count'] += 1
            
        return self.results
    
    def _crawl_url(self, url):
        """
        Crawl a single URL.
        """
        if url in self.visited_urls or self.results['pages_crawled'] >= self.source.max_pages:
            return
            
        try:
            logger.info(f"Crawling URL: {url}")
            
            # Add delay between requests
            if self.source.delay_between_requests > 0:
                import time
                time.sleep(self.source.delay_between_requests)
            
            # Make request
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            self.visited_urls.add(url)
            self.results['pages_crawled'] += 1
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract articles from the page
            articles = self._extract_articles(soup, url)
            
            for article in articles:
                self._process_article(article)
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            self.results['errors_count'] += 1
    
    def _extract_articles(self, soup, base_url):
        """
        Extract article information from a page.
        """
        articles = []
        
        # If content selector is specified, use it
        if self.source.content_selector:
            content_elements = soup.select(self.source.content_selector)
        else:
            # Default selectors for common article patterns
            content_elements = soup.select('article, .post, .entry, .content')
        
        for element in content_elements:
            try:
                article = self._extract_article_data(element, soup, base_url)
                if article and self._is_valid_article(article):
                    articles.append(article)
            except Exception as e:
                logger.error(f"Error extracting article: {str(e)}")
                continue
        
        return articles
    
    def _extract_article_data(self, element, soup, base_url):
        """
        Extract data from a single article element.
        """
        article = {}
        
        # Extract title
        if self.source.title_selector:
            title_elem = element.select_one(self.source.title_selector)
        else:
            title_elem = element.select_one('h1, h2, h3, .title, .post-title')
        
        if title_elem:
            article['title'] = title_elem.get_text().strip()
        else:
            return None
        
        # Extract content
        content_elem = element
        if self.source.content_selector:
            content_elem = element.select_one(self.source.content_selector) or element
        
        # Clean up content
        article['content'] = self._clean_content(content_elem)
        
        # Extract author
        if self.source.author_selector:
            author_elem = element.select_one(self.source.author_selector)
            if author_elem:
                article['author'] = author_elem.get_text().strip()
        
        # Extract publication date
        if self.source.date_selector:
            date_elem = element.select_one(self.source.date_selector)
            if date_elem:
                article['published_date'] = self._parse_date(date_elem.get_text().strip())
        
        # Extract URL (if it's a link to full article)
        link_elem = element.select_one('a[href]')
        if link_elem:
            article['url'] = urljoin(base_url, link_elem['href'])
        else:
            article['url'] = base_url
        
        # Store raw HTML for reference
        article['raw_html'] = str(element)
        
        return article
    
    def _clean_content(self, element):
        """
        Clean and extract text content from HTML element.
        """
        # Remove unwanted elements
        for unwanted in element.select('script, style, nav, footer, .comments, .sidebar'):
            unwanted.decompose()
        
        # Get text content
        text = element.get_text()
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _parse_date(self, date_string):
        """
        Parse date string into datetime object.
        """
        try:
            from dateutil import parser
            return parser.parse(date_string)
        except:
            return None
    
    def _is_valid_article(self, article):
        """
        Check if article meets minimum quality requirements.
        """
        # Must have title and content
        if not article.get('title') or not article.get('content'):
            return False
        
        # Content must be substantial (at least 100 characters)
        if len(article['content']) < 100:
            return False
        
        # Check URL patterns
        url = article.get('url', '')
        
        # Check include patterns
        include_patterns = self.source.get_include_patterns_list()
        if include_patterns:
            if not any(pattern in url for pattern in include_patterns):
                return False
        
        # Check exclude patterns
        exclude_patterns = self.source.get_exclude_patterns_list()
        if exclude_patterns:
            if any(pattern in url for pattern in exclude_patterns):
                return False
        
        return True
    
    def _process_article(self, article):
        """
        Process and save an extracted article.
        """
        try:
            # Generate content hash
            content_for_hash = f"{article['title']}{article['content']}".encode('utf-8')
            content_hash = hashlib.sha256(content_for_hash).hexdigest()
            
            # Check for duplicates
            if CrawledContent.objects.filter(content_hash=content_hash).exists():
                logger.info(f"Duplicate content found: {article['title']}")
                self.results['duplicates_found'] += 1
                return
            
            # Check similarity to existing posts
            similarity_score = self._calculate_similarity(article['content'])
            
            # Create crawled content record
            crawled_content = CrawledContent.objects.create(
                crawl_job=self.job,
                source_url=article.get('url', ''),
                title=article['title'],
                content=article['content'],
                author=article.get('author', ''),
                published_date=article.get('published_date'),
                content_hash=content_hash,
                similarity_score=similarity_score,
                raw_html=article.get('raw_html', ''),
                extracted_metadata={
                    'word_count': len(article['content'].split()),
                    'extraction_method': 'automated'
                }
            )
            
            self.results['posts_found'] += 1
            self.results['posts_created'] += 1
            
            logger.info(f"Created crawled content: {article['title']}")
            
        except Exception as e:
            logger.error(f"Error processing article {article.get('title', 'Unknown')}: {str(e)}")
            self.results['errors_count'] += 1
    
    def _calculate_similarity(self, content):
        """
        Calculate similarity to existing content using TF-IDF and cosine similarity.
        """
        try:
            # Get existing published posts
            existing_posts = Post.objects.filter(status='published').values_list('content', flat=True)[:100]
            
            if not existing_posts:
                return 0.0
            
            # Prepare documents for comparison
            documents = list(existing_posts) + [content]
            
            # Calculate TF-IDF vectors
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])
            
            # Return maximum similarity score
            return float(similarity_matrix.max())
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def _crawl_additional_pages(self):
        """
        Crawl additional pages by following links.
        """
        # This is a simplified implementation
        # In a real-world scenario, you'd implement more sophisticated link discovery
        pass


@shared_task
def cleanup_old_crawl_jobs():
    """
    Clean up old crawl jobs and logs.
    """
    from datetime import timedelta
    
    # Delete crawl jobs older than 30 days
    cutoff_date = django_timezone.now() - timedelta(days=30)
    old_jobs = CrawlJob.objects.filter(created_at__lt=cutoff_date)
    
    count = old_jobs.count()
    old_jobs.delete()
    
    logger.info(f"Cleaned up {count} old crawl jobs")


@shared_task
def schedule_periodic_crawls():
    """
    Schedule periodic crawls based on source configurations.
    """
    from django_celery_beat.models import PeriodicTask, CrontabSchedule
    import json
    
    active_sources = CrawlSource.objects.filter(is_active=True).exclude(schedule='manual')
    
    for source in active_sources:
        # Create or update periodic task
        task_name = f"crawl_source_{source.id}"
        
        # Define cron schedule based on source schedule
        cron_kwargs = {}
        if source.schedule == 'hourly':
            cron_kwargs = {'minute': 0}
        elif source.schedule == 'daily':
            cron_kwargs = {'hour': 2, 'minute': 0}
        elif source.schedule == 'weekly':
            cron_kwargs = {'day_of_week': 1, 'hour': 2, 'minute': 0}
        elif source.schedule == 'monthly':
            cron_kwargs = {'day_of_month': 1, 'hour': 2, 'minute': 0}
        
        if cron_kwargs:
            schedule, created = CrontabSchedule.objects.get_or_create(**cron_kwargs)
            
            # Create periodic task
            PeriodicTask.objects.update_or_create(
                name=task_name,
                defaults={
                    'task': 'apps.crawler.tasks.trigger_crawl_for_source',
                    'crontab': schedule,
                    'args': json.dumps([source.id]),
                    'enabled': True,
                }
            )


@shared_task
def trigger_crawl_for_source(source_id):
    """
    Trigger a crawl for a specific source (used by periodic tasks).
    """
    try:
        source = CrawlSource.objects.get(id=source_id)
        
        # Create crawl job
        job = CrawlJob.objects.create(source=source)
        
        # Trigger the crawl
        trigger_crawl_task.delay(job.id)
        
        logger.info(f"Triggered periodic crawl for source {source.name}")
        
    except CrawlSource.DoesNotExist:
        logger.error(f"Source {source_id} not found for periodic crawl")
    except Exception as e:
        logger.error(f"Error triggering periodic crawl for source {source_id}: {str(e)}")
