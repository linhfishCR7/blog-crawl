# Database Schema Design

This document outlines the database schema for the Blog CMS with automated web crawling capabilities.

## Overview

The database is designed to support both original content creation and automated web crawling with proper content attribution and duplicate detection.

## Core Tables

### Authentication

#### `auth_user` (Custom User Model)
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `first_name`
- `last_name`
- `bio` (Text)
- `avatar` (ImageField)
- `is_verified` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### `user_profiles`
- `id` (Primary Key)
- `user_id` (Foreign Key to auth_user)
- `website` (URL)
- `twitter`, `github`, `linkedin` (Social profiles)
- `location`
- `birth_date`
- `email_notifications` (Boolean)
- `newsletter_subscription` (Boolean)
- `created_at`, `updated_at`

### Blog Content

#### `blog_categories`
- `id` (Primary Key)
- `name` (Unique)
- `slug` (Unique, auto-generated)
- `description` (Text)
- `color` (Hex color code)
- `created_at`, `updated_at`

#### `blog_posts`
- `id` (Primary Key)
- `title`
- `slug` (Unique, auto-generated)
- `content` (Rich text)
- `excerpt`
- `author_id` (Foreign Key to auth_user)
- `category_id` (Foreign Key to blog_categories, nullable)
- `status` (draft, published, archived, pending)
- `source_type` (original, crawled)
- `is_featured` (Boolean)
- `meta_title`, `meta_description` (SEO fields)
- `featured_image` (ImageField)
- `published_at` (DateTime, nullable)
- `created_at`, `updated_at`
- `content_hash` (SHA256 for duplicate detection)
- `original_url` (For crawled content)
- `original_author` (For crawled content)
- `original_published_date` (For crawled content)
- `crawl_source_id` (Foreign Key to crawler_sources)

**Indexes:**
- `(status, published_at)` - For published content queries
- `source_type` - For filtering by content type
- `content_hash` - For duplicate detection

#### `blog_comments`
- `id` (Primary Key)
- `post_id` (Foreign Key to blog_posts)
- `author_id` (Foreign Key to auth_user)
- `content` (Text)
- `parent_id` (Self-referencing for nested comments)
- `is_approved` (Boolean)
- `created_at`, `updated_at`

#### `blog_post_views`
- `id` (Primary Key)
- `post_id` (Foreign Key to blog_posts)
- `ip_address` (GenericIPAddressField)
- `user_agent` (Text)
- `user_id` (Foreign Key to auth_user, nullable)
- `created_at`

**Unique Constraint:** `(post_id, ip_address, user_id)`

### Web Crawling

#### `crawler_sources`
- `id` (Primary Key)
- `name`
- `url` (Target website URL)
- `description` (Text)
- `schedule` (manual, hourly, daily, weekly, monthly)
- `is_active` (Boolean)
- `status` (active, inactive, error)
- `content_selector`, `title_selector`, `author_selector`, `date_selector` (CSS selectors)
- `max_pages` (Integer)
- `delay_between_requests` (Float)
- `follow_links` (Boolean)
- `include_patterns`, `exclude_patterns` (Text, newline-separated)
- `created_by_id` (Foreign Key to auth_user)
- `created_at`, `updated_at`
- `last_crawled_at` (DateTime, nullable)
- `total_crawls`, `successful_crawls`, `failed_crawls` (Statistics)
- `total_posts_found` (Integer)

#### `crawler_jobs`
- `id` (Primary Key)
- `source_id` (Foreign Key to crawler_sources)
- `status` (pending, running, completed, failed, cancelled)
- `started_at`, `completed_at` (DateTime, nullable)
- `duration` (DurationField)
- `pages_crawled`, `posts_found`, `posts_created`, `posts_updated` (Integers)
- `duplicates_found`, `errors_count` (Integers)
- `log_data` (JSONField for structured logs)
- `error_message` (Text)
- `triggered_by_id` (Foreign Key to auth_user, nullable)
- `created_at`

#### `crawler_content`
- `id` (Primary Key)
- `crawl_job_id` (Foreign Key to crawler_jobs)
- `source_url`
- `title`
- `content` (Text)
- `author`
- `published_date` (DateTime, nullable)
- `status` (pending, approved, rejected, processed)
- `content_hash` (SHA256 for duplicate detection)
- `similarity_score` (Float, 0-1 for content similarity)
- `raw_html` (Text, original HTML)
- `extracted_metadata` (JSONField)
- `processed_by_id` (Foreign Key to auth_user, nullable)
- `processed_at` (DateTime, nullable)
- `blog_post_id` (Foreign Key to blog_posts, nullable)
- `created_at`, `updated_at`

**Indexes:**
- `content_hash` - For duplicate detection
- `status` - For filtering pending content
- `similarity_score` - For finding similar content

#### `crawler_schedules`
- `id` (Primary Key)
- `source_id` (OneToOne to crawler_sources)
- `celery_task_id` (Celery periodic task ID)
- `is_active` (Boolean)
- `cron_expression`
- `next_run_time` (DateTime, nullable)
- `created_at`, `updated_at`

### Tags (Django-taggit)

#### `taggit_tag`
- `id` (Primary Key)
- `name` (Unique)
- `slug` (Unique)

#### `taggit_taggeditem`
- `id` (Primary Key)
- `tag_id` (Foreign Key to taggit_tag)
- `object_id` (Generic foreign key)
- `content_type_id` (Foreign Key to django_content_type)

### Celery Beat (django-celery-beat)

#### `django_celery_beat_periodictask`
- Stores periodic task definitions for scheduled crawling

#### `django_celery_beat_crontabschedule`
- Stores cron schedule definitions

## Relationships

### One-to-Many
- User → Posts (author)
- User → Comments (author)
- User → CrawlSources (created_by)
- Category → Posts
- Post → Comments
- Post → PostViews
- CrawlSource → CrawlJobs
- CrawlSource → Posts (crawl_source)
- CrawlJob → CrawledContent

### One-to-One
- User → UserProfile
- CrawlSource → CrawlSchedule

### Many-to-Many
- Post → Tags (through taggit)

## Data Integrity Features

### Duplicate Detection
1. **Content Hashing**: SHA256 hash of title + content
2. **Similarity Scoring**: TF-IDF cosine similarity (0-1 scale)
3. **URL Deduplication**: Prevent crawling same URLs multiple times

### Content Attribution
- Original source URL preservation
- Author information retention
- Publication date tracking
- Source website attribution

### Audit Trail
- Creation and modification timestamps on all entities
- User tracking for content creation and approval
- Crawl job logging and error tracking

## Performance Optimizations

### Database Indexes
- Composite indexes on frequently queried fields
- Hash indexes for duplicate detection
- Partial indexes for published content

### Query Optimization
- Select related for foreign key relationships
- Prefetch related for reverse foreign keys
- Database-level pagination

### Caching Strategy
- Redis caching for frequently accessed data
- Query result caching
- Template fragment caching

## Scalability Considerations

### Horizontal Scaling
- Read replicas for content delivery
- Separate databases for crawling and content serving
- Sharding by content type or date

### Data Archival
- Automatic cleanup of old crawl jobs
- Content archival for old posts
- Log rotation and cleanup

### Monitoring
- Database performance metrics
- Query execution time tracking
- Storage usage monitoring

## Security Features

### Data Protection
- Encrypted sensitive fields
- Secure password hashing
- SQL injection prevention through ORM

### Access Control
- Role-based permissions
- Content approval workflow
- API authentication and authorization

### Privacy Compliance
- User data anonymization options
- Content removal mechanisms
- GDPR compliance features
