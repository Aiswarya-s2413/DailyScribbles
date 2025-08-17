from django.urls import path, include
from . import views

app_name = 'blog'

# API URLs
api_urlpatterns = [
    path('posts/', views.api_posts_list, name='api-posts-list'),
    path('posts/<slug:slug>/', views.api_post_detail, name='api-post-detail'),
    path('categories/', views.api_categories_list, name='api-categories-list'),
    path('posts/<slug:slug>/comment/', views.api_add_comment, name='api-add-comment'),
]

# Frontend Template URLs
frontend_urlpatterns = [
    path('', views.blog_list_view, name='post_list'),
    path('post/<slug:slug>/', views.blog_detail_view, name='post_detail'),
    path('category/<slug:slug>/', views.category_view, name='category_posts'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('post/<slug:slug>/like/', views.toggle_like, name='toggle_like'),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('', include(frontend_urlpatterns)),
]