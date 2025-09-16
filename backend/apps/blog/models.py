from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
import hashlib

User = get_user_model()


class Category(models.Model):
    """
    Blog post categories.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    """
    Blog posts - both original and crawled content.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
        ('pending', 'Pending Review'),  # For crawled content
    ]

    SOURCE_CHOICES = [
        ('original', 'Original Content'),
        ('crawled', 'Crawled Content'),
    ]

    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = RichTextUploadingField()
    excerpt = models.TextField(max_length=500, blank=True)
    
    # Metadata
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = TaggableManager(blank=True)
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='original')
    is_featured = models.BooleanField(default=False)
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Media
    featured_image = models.ImageField(upload_to='posts/', blank=True, null=True)
    
    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Content fingerprinting for duplicate detection
    content_hash = models.CharField(max_length=64, blank=True, db_index=True)
    
    # Crawled content specific fields
    original_url = models.URLField(blank=True, null=True)
    original_author = models.CharField(max_length=200, blank=True)
    original_published_date = models.DateTimeField(null=True, blank=True)
    crawl_source = models.ForeignKey('crawler.CrawlSource', on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='posts')

    class Meta:
        db_table = 'blog_posts'
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['source_type']),
            models.Index(fields=['content_hash']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Generate content hash for duplicate detection
        if self.content:
            content_for_hash = f"{self.title}{self.content}".encode('utf-8')
            self.content_hash = hashlib.sha256(content_for_hash).hexdigest()
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        """Estimate reading time in minutes."""
        word_count = len(self.content.split())
        return max(1, word_count // 200)  # Assuming 200 words per minute


class Comment(models.Model):
    """
    Blog post comments.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='replies')
    
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'


class PostView(models.Model):
    """
    Track post views for analytics.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blog_post_views'
        verbose_name = 'Post View'
        verbose_name_plural = 'Post Views'
        unique_together = ['post', 'ip_address', 'user']

    def __str__(self):
        return f'View of {self.post.title}'
