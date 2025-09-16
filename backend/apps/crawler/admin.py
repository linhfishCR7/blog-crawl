from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CrawlSource, CrawlJob, CrawledContent, CrawlSchedule


@admin.register(CrawlSource)
class CrawlSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_display', 'schedule', 'is_active', 'status', 'success_rate_display', 'last_crawled_at')
    list_filter = ('schedule', 'is_active', 'status', 'created_at', 'last_crawled_at')
    search_fields = ('name', 'url', 'description')
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'last_crawled_at', 
                      'total_crawls', 'successful_crawls', 'failed_crawls', 'total_posts_found')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'url', 'description', 'schedule', 'is_active', 'status')
        }),
        ('Content Selectors', {
            'fields': ('content_selector', 'title_selector', 'author_selector', 'date_selector'),
            'classes': ('collapse',)
        }),
        ('Crawling Settings', {
            'fields': ('max_pages', 'delay_between_requests', 'follow_links'),
            'classes': ('collapse',)
        }),
        ('Filtering', {
            'fields': ('include_patterns', 'exclude_patterns'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_crawls', 'successful_crawls', 'failed_crawls', 'total_posts_found'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'last_crawled_at'),
            'classes': ('collapse',)
        })
    )
    
    def url_display(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url[:50] + '...' if len(obj.url) > 50 else obj.url)
    url_display.short_description = 'URL'
    
    def success_rate_display(self, obj):
        rate = obj.success_rate
        color = 'green' if rate >= 80 else 'orange' if rate >= 50 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)
    success_rate_display.short_description = 'Success Rate'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CrawlJob)
class CrawlJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'status', 'started_at', 'duration', 'pages_crawled', 
                   'posts_found', 'posts_created', 'duplicates_found', 'errors_count')
    list_filter = ('status', 'started_at', 'completed_at')
    search_fields = ('source__name', 'error_message')
    readonly_fields = ('source', 'started_at', 'completed_at', 'duration', 'pages_crawled',
                      'posts_found', 'posts_created', 'posts_updated', 'duplicates_found',
                      'errors_count', 'log_data', 'error_message', 'triggered_by', 'created_at')
    
    fieldsets = (
        ('Job Information', {
            'fields': ('source', 'status', 'triggered_by', 'created_at')
        }),
        ('Execution', {
            'fields': ('started_at', 'completed_at', 'duration')
        }),
        ('Results', {
            'fields': ('pages_crawled', 'posts_found', 'posts_created', 'posts_updated', 
                      'duplicates_found', 'errors_count')
        }),
        ('Logs & Errors', {
            'fields': ('log_data', 'error_message'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(CrawledContent)
class CrawledContentAdmin(admin.ModelAdmin):
    list_display = ('title_display', 'source_url_display', 'status', 'similarity_score', 
                   'is_duplicate', 'created_at')
    list_filter = ('status', 'created_at', 'similarity_score')
    search_fields = ('title', 'content', 'source_url', 'author')
    readonly_fields = ('crawl_job', 'content_hash', 'similarity_score', 'raw_html',
                      'extracted_metadata', 'processed_by', 'processed_at', 'blog_post',
                      'created_at', 'updated_at')
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'author', 'published_date')
        }),
        ('Source', {
            'fields': ('crawl_job', 'source_url')
        }),
        ('Processing', {
            'fields': ('status', 'processed_by', 'processed_at', 'blog_post')
        }),
        ('Analysis', {
            'fields': ('content_hash', 'similarity_score', 'extracted_metadata'),
            'classes': ('collapse',)
        }),
        ('Raw Data', {
            'fields': ('raw_html',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def title_display(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_display.short_description = 'Title'
    
    def source_url_display(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', 
                          obj.source_url, 
                          obj.source_url[:30] + '...' if len(obj.source_url) > 30 else obj.source_url)
    source_url_display.short_description = 'Source URL'
    
    actions = ['approve_content', 'reject_content']
    
    def approve_content(self, request, queryset):
        for content in queryset.filter(status='pending'):
            # This would typically create a blog post
            content.status = 'approved'
            content.processed_by = request.user
            content.save()
        self.message_user(request, f'{queryset.count()} content items approved.')
    approve_content.short_description = 'Approve selected content'
    
    def reject_content(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} content items rejected.')
    reject_content.short_description = 'Reject selected content'


@admin.register(CrawlSchedule)
class CrawlScheduleAdmin(admin.ModelAdmin):
    list_display = ('source', 'is_active', 'cron_expression', 'next_run_time', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('source__name',)
    readonly_fields = ('celery_task_id', 'created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return False
