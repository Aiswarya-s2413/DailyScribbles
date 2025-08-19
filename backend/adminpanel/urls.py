from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/block/', views.block_user, name='block_user'),
    path('users/<int:user_id>/unblock/', views.unblock_user, name='unblock_user'),
    
    # Blog Management URLs
    path('blogs/', views.blog_management, name='blog_management'),
    path('blogs/create/', views.create_blog, name='create_blog'),
    path('blogs/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('blogs/<int:blog_id>/edit/', views.edit_blog, name='edit_blog'),
    path('blogs/<int:blog_id>/delete/', views.delete_blog, name='delete_blog'),
    path('blogs/<int:blog_id>/attachments/delete/<int:attachment_id>/', views.delete_attachment, name='delete_attachment'),
    # Comment moderation
    path('blogs/<int:blog_id>/comments/<int:comment_id>/approve/', views.approve_comment, name='approve_comment'),
    path('blogs/<int:blog_id>/comments/<int:comment_id>/reject/', views.reject_comment, name='reject_comment'),
    
    # Comment Management URLs
    path('comments/', views.comment_management, name='comment_management'),
    path('comments/bulk-approve/', views.bulk_approve_comments, name='bulk_approve_comments'),
    path('comments/bulk-reject/', views.bulk_reject_comments, name='bulk_reject_comments'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Category Management URLs
    path('categories/', views.category_management, name='category_management'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
]