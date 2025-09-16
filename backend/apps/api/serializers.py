"""
API Serializers for the blog CMS.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from taggit.serializers import TagListSerializerField, TaggitSerializer

from apps.blog.models import Post, Category, Comment
from apps.crawler.models import CrawlSource, CrawlJob, CrawledContent
from apps.authentication.models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer.
    """
    class Meta:
        model = UserProfile
        fields = [
            'website', 'twitter', 'github', 'linkedin', 'location',
            'birth_date', 'email_notifications', 'newsletter_subscription'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer with profile information.
    """
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'bio', 'avatar', 'is_verified', 'profile',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User registration serializer.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Create user profile
        UserProfile.objects.create(user=user)
        return user


class CategorySerializer(serializers.ModelSerializer):
    """
    Category serializer.
    """
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'color',
            'post_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_post_count(self, obj):
        return obj.post_set.filter(status='published').count()


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    """
    Blog post serializer.
    """
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    tags = TagListSerializerField()
    reading_time = serializers.ReadOnlyField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author', 'category',
            'category_id', 'tags', 'status', 'source_type', 'is_featured',
            'meta_title', 'meta_description', 'featured_image', 'reading_time',
            'comment_count', 'published_at', 'created_at', 'updated_at',
            'original_url', 'original_author', 'original_published_date'
        ]
        read_only_fields = [
            'id', 'slug', 'author', 'reading_time', 'comment_count',
            'created_at', 'updated_at'
        ]

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer.
    """
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'content', 'parent', 'replies',
            'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'is_approved', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(is_approved=True), many=True).data
        return []


class CrawlSourceSerializer(serializers.ModelSerializer):
    """
    Crawl source serializer.
    """
    created_by = UserSerializer(read_only=True)
    success_rate = serializers.ReadOnlyField()
    include_patterns_list = serializers.ReadOnlyField()
    exclude_patterns_list = serializers.ReadOnlyField()

    class Meta:
        model = CrawlSource
        fields = [
            'id', 'name', 'url', 'description', 'schedule', 'is_active', 'status',
            'content_selector', 'title_selector', 'author_selector', 'date_selector',
            'max_pages', 'delay_between_requests', 'follow_links',
            'include_patterns', 'exclude_patterns', 'include_patterns_list',
            'exclude_patterns_list', 'created_by', 'created_at', 'updated_at',
            'last_crawled_at', 'total_crawls', 'successful_crawls', 'failed_crawls',
            'total_posts_found', 'success_rate'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at', 'last_crawled_at',
            'total_crawls', 'successful_crawls', 'failed_crawls', 'total_posts_found',
            'success_rate', 'include_patterns_list', 'exclude_patterns_list'
        ]


class CrawlJobSerializer(serializers.ModelSerializer):
    """
    Crawl job serializer.
    """
    source = CrawlSourceSerializer(read_only=True)
    triggered_by = UserSerializer(read_only=True)
    is_running = serializers.ReadOnlyField()

    class Meta:
        model = CrawlJob
        fields = [
            'id', 'source', 'status', 'started_at', 'completed_at', 'duration',
            'pages_crawled', 'posts_found', 'posts_created', 'posts_updated',
            'duplicates_found', 'errors_count', 'log_data', 'error_message',
            'triggered_by', 'created_at', 'is_running'
        ]
        read_only_fields = [
            'id', 'source', 'triggered_by', 'created_at', 'is_running'
        ]


class CrawledContentSerializer(serializers.ModelSerializer):
    """
    Crawled content serializer.
    """
    crawl_job = CrawlJobSerializer(read_only=True)
    processed_by = UserSerializer(read_only=True)
    is_duplicate = serializers.ReadOnlyField()

    class Meta:
        model = CrawledContent
        fields = [
            'id', 'crawl_job', 'source_url', 'title', 'content', 'author',
            'published_date', 'status', 'content_hash', 'similarity_score',
            'extracted_metadata', 'processed_by', 'processed_at', 'blog_post',
            'created_at', 'updated_at', 'is_duplicate'
        ]
        read_only_fields = [
            'id', 'crawl_job', 'content_hash', 'processed_by', 'processed_at',
            'blog_post', 'created_at', 'updated_at', 'is_duplicate'
        ]
