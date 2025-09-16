# Blog CMS Setup Guide

This guide will help you set up the Blog CMS with automated web crawling capabilities.

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blog-crawl
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your specific configuration.

3. **Start the development environment**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - Admin Panel: http://localhost:8000/admin
   - API Documentation: http://localhost:8000/api/docs

## Initial Configuration

### 1. Set up Crawl Sources

1. Log in to the admin panel at http://localhost:8000/admin
2. Navigate to "Crawl Sources" under the "Crawler" section
3. Add the initial target websites:
   - https://theorangeone.net/posts/tags/django/
   - https://hakibenita.com/
   - https://ilovedjango.com/
   - https://testdriven.io/blog/topics/django-rest-framework/
   - https://testdriven.io/blog/topics/django/

### 2. Configure Crawling Settings

For each crawl source, configure:
- **Schedule**: How often to crawl (hourly, daily, weekly, monthly)
- **Content Selectors**: CSS selectors for extracting content
- **Rate Limiting**: Delay between requests to be respectful
- **URL Patterns**: Include/exclude patterns for filtering URLs

### 3. Test Manual Crawling

1. Go to the frontend at http://localhost:3000
2. Navigate to "Crawl Sources"
3. Trigger a manual crawl to test the configuration
4. Monitor the crawl job progress in "Crawl Jobs"
5. Review extracted content in "Crawled Content"

## Development

### Backend Development

The Django backend is located in the `backend/` directory:

```bash
# Install dependencies
cd backend
pip install -r requirements/development.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Development

The React frontend is located in the `frontend/` directory:

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start
```

### Running Tests

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests
docker-compose exec frontend npm test
```

## Production Deployment

### Environment Variables

Update the `.env` file for production:

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (use PostgreSQL in production)
DB_NAME=blog_cms_prod
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_HOST=your_db_host
DB_PORT=5432

# Redis
REDIS_URL=redis://your-redis-host:6379/0

# Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## Monitoring and Maintenance

### Crawl Job Monitoring

- Monitor crawl jobs through the admin panel or API
- Set up alerts for failed crawls
- Review crawl logs for debugging

### Content Review Workflow

1. Crawled content appears in "Pending Review" status
2. Review content for quality and relevance
3. Approve content to convert to blog posts
4. Reject inappropriate or duplicate content

### Database Maintenance

```bash
# Clean up old crawl jobs (runs automatically via Celery)
docker-compose exec backend python manage.py shell -c "
from apps.crawler.tasks import cleanup_old_crawl_jobs
cleanup_old_crawl_jobs.delay()
"
```

## Troubleshooting

### Common Issues

1. **Crawl jobs failing**
   - Check robots.txt compliance
   - Verify CSS selectors are correct
   - Ensure target websites are accessible
   - Review error logs in crawl job details

2. **Database connection errors**
   - Verify database credentials in `.env`
   - Ensure PostgreSQL service is running
   - Check network connectivity

3. **Frontend not loading**
   - Verify API URL in frontend environment
   - Check CORS settings in Django
   - Ensure backend is running and accessible

### Logs

```bash
# View backend logs
docker-compose logs backend

# View frontend logs
docker-compose logs frontend

# View Celery worker logs
docker-compose logs celery

# View database logs
docker-compose logs db
```

## Legal Compliance

### Content Attribution

The system automatically:
- Stores original source URLs
- Preserves author information
- Adds "noindex" meta tags to crawled content
- Displays source attribution on all crawled posts

### Robots.txt Compliance

- The crawler respects robots.txt by default
- Configure `RESPECT_ROBOTS_TXT=True` in settings
- Set appropriate crawl delays between requests

### Content Removal

To remove content upon request:
1. Identify the content in the admin panel
2. Delete the blog post and associated crawled content
3. Add the source URL to exclude patterns to prevent re-crawling

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/api/docs`
3. Check the Django admin panel for detailed error messages
4. Review application logs for debugging information
