# Blog CMS with Automated Web Crawling

A comprehensive Content Management System with automated web crawling capabilities for aggregating and managing blog content from multiple sources.

## Features

### Core CMS Features
- User authentication and authorization system
- Complete blog functionality: create, edit, delete, and publish posts
- Rich text editor for content creation
- Content management dashboard with search and filtering
- Post categorization and tagging system
- SEO-friendly URLs and metadata management

### Web Crawling Features
- Automated web crawling from external websites using configurable schedules
- Manual trigger functionality for immediate crawling
- Flexible scheduling options: hourly, daily, weekly, monthly intervals
- Web interface to manage target websites for crawling
- Intelligent duplicate content detection
- Robust error handling and logging
- Rate limiting and respectful crawling (robots.txt compliance)

### Legal Compliance
- Source attribution with clickable links to original articles
- Original publication dates and author information preservation
- "noindex" meta tags for crawled content
- Content removal mechanism upon request

## Technology Stack

- **Backend:** Django + Django REST Framework
- **Task Queue:** Celery + Redis
- **Database:** PostgreSQL
- **Frontend:** React + TypeScript
- **Web Crawling:** Scrapy + BeautifulSoup
- **Containerization:** Docker
- **Web Server:** Nginx

## Project Structure

```
blog-crawl/
├── backend/                 # Django backend application
│   ├── blog_cms/           # Main Django project
│   ├── apps/               # Django applications
│   │   ├── authentication/ # User management
│   │   ├── blog/           # Blog functionality
│   │   ├── crawler/        # Web crawling system
│   │   └── api/            # REST API endpoints
│   ├── requirements/       # Python dependencies
│   └── manage.py
├── frontend/               # React frontend application
│   ├── src/
│   ├── public/
│   └── package.json
├── crawler/                # Scrapy crawling framework
│   ├── spiders/
│   └── scrapy.cfg
├── docker/                 # Docker configuration
├── nginx/                  # Nginx configuration
└── docker-compose.yml      # Development environment
```

## Getting Started

1. Clone the repository
2. Copy environment variables: `cp .env.example .env`
3. Start development environment: `docker-compose up -d`
4. Run migrations: `docker-compose exec backend python manage.py migrate`
5. Create superuser: `docker-compose exec backend python manage.py createsuperuser`
6. Access the application at http://localhost:3000

## Initial Target Websites

- https://theorangeone.net/posts/tags/django/
- https://hakibenita.com/
- https://ilovedjango.com/
- https://testdriven.io/blog/topics/django-rest-framework/
- https://testdriven.io/blog/topics/django/

## License

MIT License - see LICENSE file for details.
