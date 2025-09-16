"""
API Views for the blog CMS.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from apps.blog.models import Post, Category, Comment
from apps.crawler.models import CrawlSource, CrawlJob, CrawledContent
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    PostSerializer, CategorySerializer, CommentSerializer,
    CrawlSourceSerializer, CrawlJobSerializer, CrawledContentSerializer,
)
from apps.crawler.tasks import trigger_crawl_task

User = get_user_model()


class RegisterView(APIView):
    """
    User registration endpoint.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': UserSerializer(user).data,
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    User management viewset.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list' and not self.request.user.is_staff:
            return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """Get or update current user profile."""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ModelViewSet):
    """
    Blog post management viewset.
    """
    queryset = Post.objects.filter(status='published')
    serializer_class = PostSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Post.objects.all()
        
        # Filter by status for non-staff users
        if not self.request.user.is_staff:
            if self.action == 'list':
                queryset = queryset.filter(status='published')
            elif self.action in ['update', 'partial_update', 'destroy']:
                queryset = queryset.filter(author=self.request.user)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by tag
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__name=tag)
        
        # Filter by source type
        source_type = self.request.query_params.get('source_type')
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, slug=None):
        """Publish a draft post."""
        post = self.get_object()
        if post.author != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        post.status = 'published'
        post.save()
        return Response({'message': 'Post published successfully'})


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Category management viewset.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class CommentViewSet(viewsets.ModelViewSet):
    """
    Comment management viewset.
    """
    queryset = Comment.objects.filter(is_approved=True)
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Comment.objects.all()
        
        # Filter by post
        post_slug = self.request.query_params.get('post')
        if post_slug:
            queryset = queryset.filter(post__slug=post_slug)
        
        # Show only approved comments for non-staff users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        return queryset.order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CrawlSourceViewSet(viewsets.ModelViewSet):
    """
    Crawl source management viewset.
    """
    queryset = CrawlSource.objects.all()
    serializer_class = CrawlSourceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def trigger_crawl(self, request, pk=None):
        """Manually trigger a crawl for this source."""
        source = self.get_object()
        
        # Create and trigger crawl job
        job = CrawlJob.objects.create(
            source=source,
            triggered_by=request.user
        )
        
        # Trigger the crawl task
        trigger_crawl_task.delay(job.id)
        
        return Response({
            'message': 'Crawl job triggered successfully',
            'job_id': job.id
        })


class CrawlJobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Crawl job monitoring viewset.
    """
    queryset = CrawlJob.objects.all()
    serializer_class = CrawlJobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CrawlJob.objects.all()
        
        # Filter by source
        source_id = self.request.query_params.get('source')
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


class CrawledContentViewSet(viewsets.ModelViewSet):
    """
    Crawled content management viewset.
    """
    queryset = CrawledContent.objects.all()
    serializer_class = CrawledContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CrawledContent.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by job
        job_id = self.request.query_params.get('job')
        if job_id:
            queryset = queryset.filter(crawl_job_id=job_id)
        
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve crawled content and convert to blog post."""
        content = self.get_object()
        
        if content.status != 'pending':
            return Response({'error': 'Content is not pending approval'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create blog post from crawled content
        post = Post.objects.create(
            title=content.title,
            content=content.content,
            author=request.user,
            status='pending',
            source_type='crawled',
            original_url=content.source_url,
            original_author=content.author,
            original_published_date=content.published_date,
            crawl_source=content.crawl_job.source,
            content_hash=content.content_hash
        )
        
        # Update crawled content status
        content.status = 'processed'
        content.processed_by = request.user
        content.blog_post = post
        content.save()
        
        return Response({
            'message': 'Content approved and converted to blog post',
            'post_id': post.id
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject crawled content."""
        content = self.get_object()
        content.status = 'rejected'
        content.processed_by = request.user
        content.save()
        
        return Response({'message': 'Content rejected'})


class TriggerCrawlView(APIView):
    """
    Manually trigger crawl jobs.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        source_id = request.data.get('source_id')
        if not source_id:
            return Response({'error': 'source_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        source = get_object_or_404(CrawlSource, id=source_id)
        
        # Create crawl job
        job = CrawlJob.objects.create(
            source=source,
            triggered_by=request.user
        )
        
        # Trigger the crawl task
        trigger_crawl_task.delay(job.id)
        
        return Response({
            'message': 'Crawl job triggered successfully',
            'job_id': job.id
        })
