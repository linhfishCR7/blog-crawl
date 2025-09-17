from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.utils import timezone
import json

User = get_user_model()


class CrawlSource(models.Model):
    """
    Websites and URLs to crawl for content.
    """
    SCHEDULE_CHOICES = [
        ('manual', 'Manual Only'),
        ('hourly', 'Every Hour'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]

    # Basic information
    name = models.CharField(max_length=200)
    url = models.URLField(validators=[URLValidator()])
    description = models.TextField(blank=True)
    
    # Crawling configuration
    schedule = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default='daily')
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Crawling rules and selectors
    content_selector = models.CharField(max_length=500, blank=True, 
                                      help_text='CSS selector for main content')
    title_selector = models.CharField(max_length=500, blank=True,
                                    help_text='CSS selector for article title')
    author_selector = models.CharField(max_length=500, blank=True,
                                     help_text='CSS selector for author name')
    date_selector = models.CharField(max_length=500, blank=True,
                                   help_text='CSS selector for publication date')
    
    # Advanced settings
    max_pages = models.PositiveIntegerField(default=10, 
                                          help_text='Maximum pages to crawl per session')
    delay_between_requests = models.FloatField(default=1.0,
                                             help_text='Delay in seconds between requests')
    follow_links = models.BooleanField(default=True,
                                     help_text='Follow internal links to find more content')
    
    # Filtering
    include_patterns = models.TextField(blank=True,
                                      help_text='URL patterns to include (one per line)')
    exclude_patterns = models.TextField(blank=True,
                                      help_text='URL patterns to exclude (one per line)')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crawl_sources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_crawled_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_crawls = models.PositiveIntegerField(default=0)
    successful_crawls = models.PositiveIntegerField(default=0)
    failed_crawls = models.PositiveIntegerField(default=0)
    total_posts_found = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'crawler_sources'
        verbose_name = 'Crawl Source'
        verbose_name_plural = 'Crawl Sources'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def success_rate(self):
        """Calculate crawl success rate as percentage."""
        if self.total_crawls == 0:
            return 0
        return (self.successful_crawls / self.total_crawls) * 100

    def get_include_patterns_list(self):
        """Get include patterns as a list."""
        if not self.include_patterns:
            return []
        return [pattern.strip() for pattern in self.include_patterns.split('\n') if pattern.strip()]

    def get_exclude_patterns_list(self):
        """Get exclude patterns as a list."""
        if not self.exclude_patterns:
            return []
        return [pattern.strip() for pattern in self.exclude_patterns.split('\n') if pattern.strip()]


class CrawlJob(models.Model):
    """
    Individual crawl job instances.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    source = models.ForeignKey(CrawlSource, on_delete=models.CASCADE, related_name='crawl_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Job details
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Results
    pages_crawled = models.PositiveIntegerField(default=0)
    posts_found = models.PositiveIntegerField(default=0)
    posts_created = models.PositiveIntegerField(default=0)
    posts_updated = models.PositiveIntegerField(default=0)
    duplicates_found = models.PositiveIntegerField(default=0)
    errors_count = models.PositiveIntegerField(default=0)
    
    # Logs and errors
    log_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Metadata
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='triggered_crawl_jobs')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crawler_jobs'
        verbose_name = 'Crawl Job'
        verbose_name_plural = 'Crawl Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f'Crawl job for {self.source.name} - {self.status}'

    @property
    def is_running(self):
        return self.status in ['pending', 'running']

    def add_log_entry(self, level, message, **extra_data):
        """Add a log entry to the job."""
        if not isinstance(self.log_data, list):
            self.log_data = []
        
        log_entry = {
            'timestamp': str(timezone.now()),
            'level': level,
            'message': message,
            **extra_data
        }
        self.log_data.append(log_entry)
        self.save(update_fields=['log_data'])


class CrawledContent(models.Model):
    """
    Raw crawled content before processing into blog posts.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed into Post'),
    ]

    # Source information
    crawl_job = models.ForeignKey(CrawlJob, on_delete=models.CASCADE, related_name='crawled_content')
    source_url = models.URLField()
    
    # Content
    title = models.CharField(max_length=500)
    content = models.TextField()
    author = models.CharField(max_length=200, blank=True)
    published_date = models.DateTimeField(null=True, blank=True)
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    content_hash = models.CharField(max_length=64, db_index=True)
    similarity_score = models.FloatField(null=True, blank=True,
                                       help_text='Similarity to existing content (0-1)')
    
    # Metadata
    raw_html = models.TextField(blank=True)
    extracted_metadata = models.JSONField(default=dict, blank=True)
    
    # Processing information
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_crawled_content')
    processed_at = models.DateTimeField(null=True, blank=True)
    blog_post = models.ForeignKey('blog.Post', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crawler_content'
        verbose_name = 'Crawled Content'
        verbose_name_plural = 'Crawled Content'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_hash']),
            models.Index(fields=['status']),
            models.Index(fields=['similarity_score']),
        ]

    def __str__(self):
        return f'{self.title[:50]}... - {self.status}'

    @property
    def is_duplicate(self):
        """Check if this content is likely a duplicate."""
        return self.similarity_score and self.similarity_score > 0.8


class CrawlSchedule(models.Model):
    """
    Scheduled crawl tasks using django-celery-beat.
    """
    source = models.OneToOneField(CrawlSource, on_delete=models.CASCADE, related_name='crawl_schedule')
    celery_task_id = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Schedule configuration
    cron_expression = models.CharField(max_length=100, blank=True)
    next_run_time = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crawler_schedules'
        verbose_name = 'Crawl Schedule'
        verbose_name_plural = 'Crawl Schedules'

    def __str__(self):
        return f'Schedule for {self.source.name}'
