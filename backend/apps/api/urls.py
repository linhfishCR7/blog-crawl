"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    # Authentication
    UserViewSet,
    RegisterView,
    
    # Blog
    PostViewSet,
    CategoryViewSet,
    CommentViewSet,
    
    # Crawler
    CrawlSourceViewSet,
    CrawlJobViewSet,
    CrawledContentViewSet,
    TriggerCrawlView,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'crawl-sources', CrawlSourceViewSet)
router.register(r'crawl-jobs', CrawlJobViewSet)
router.register(r'crawled-content', CrawledContentViewSet)

urlpatterns = [
    # Authentication
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    # Crawler actions
    path('crawler/trigger/', TriggerCrawlView.as_view(), name='trigger_crawl'),
    
    # Include router URLs
    path('', include(router.urls)),
]
