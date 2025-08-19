from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from blog.models import BlogPost, Category, BlogPostAttachment, Comment
import json

User = get_user_model()


def is_admin(user):
    """Check if user is admin (staff or superuser)"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def admin_login(request):
    """Admin login page"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('adminpanel:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and is_admin(user):
            login(request, user)
            messages.success(request, 'Welcome to Admin Panel!')
            return redirect('adminpanel:dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'adminpanel/login.html')


@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    """Admin logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('adminpanel:login')


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard"""
    # Get some basic stats
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    blocked_users = User.objects.filter(is_active=False).count()
    
    # Blog stats
    total_blogs = BlogPost.objects.count()
    published_blogs = BlogPost.objects.filter(status='published').count()
    draft_blogs = BlogPost.objects.filter(status='draft').count()
    total_categories = Category.objects.count()
    total_comments = Comment.objects.count()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'blocked_users': blocked_users,
        'total_blogs': total_blogs,
        'published_blogs': published_blogs,
        'draft_blogs': draft_blogs,
        'total_categories': total_categories,
        'total_comments': total_comments,
    }
    return render(request, 'adminpanel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def user_management(request):
    """User management page"""
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', 'all')
    
    # Base queryset
    users = User.objects.all().order_by('-date_joined')
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Apply status filter
    if filter_type == 'active':
        users = users.filter(is_active=True)
    elif filter_type == 'inactive':
        users = users.filter(is_active=False)
    elif filter_type == 'staff':
        users = users.filter(is_staff=True)
    
    # Pagination
    paginator = Paginator(users, 20)  # Show 20 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_type': filter_type,
        'total_users': users.count(),
    }
    return render(request, 'adminpanel/user_management.html', context)


@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    """User detail and edit page"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Update user information
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        
        # Handle password change
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        try:
            user.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('adminpanel:user_detail', user_id=user.id)
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    # Get user's blog posts and comments count
    user_posts_count = user.blog_posts.count() if hasattr(user, 'blog_posts') else 0
    user_comments_count = user.comments.count() if hasattr(user, 'comments') else 0
    
    context = {
        'user_obj': user,  # Using user_obj to avoid conflict with request.user
        'user_posts_count': user_posts_count,
        'user_comments_count': user_comments_count,
    }
    return render(request, 'adminpanel/user_detail.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_user(request, user_id):
    """Delete user"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deleting yourself
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('adminpanel:user_management')
    
    # Prevent deleting superusers (unless you are one)
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'You cannot delete a superuser.')
        return redirect('adminpanel:user_management')
    
    username = user.username
    user.delete()
    messages.success(request, f'User {username} has been deleted successfully.')
    return redirect('adminpanel:user_management')


@login_required
@user_passes_test(is_admin)
def create_user(request):
    """Create new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active', 'on') == 'on'
        
        # Validation
        if not username or not email or not password:
            messages.error(request, 'Username, email, and password are required.')
            return render(request, 'adminpanel/create_user.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'adminpanel/create_user.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'adminpanel/create_user.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.is_staff = is_staff
            user.is_active = is_active
            user.save()
            
            messages.success(request, f'User {username} created successfully!')
            return redirect('adminpanel:user_detail', user_id=user.id)
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    return render(request, 'adminpanel/create_user.html')


@login_required
@user_passes_test(is_admin)
@require_POST
def block_user(request, user_id):
    """Block user (set is_active=False)"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent blocking yourself
    if user == request.user:
        messages.error(request, 'You cannot block your own account.')
        return redirect('adminpanel:user_management')
    
    # Prevent blocking superusers (unless you are one)
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'You cannot block a superuser.')
        return redirect('adminpanel:user_management')
    
    # Block the user
    user.is_active = False
    user.save()
    
    messages.success(request, f'User {user.username} has been blocked successfully. They will not be able to login.')
    
    # Redirect back to the referring page
    referer = request.META.get('HTTP_REFERER')
    if referer and 'user_detail' in referer:
        return redirect('adminpanel:user_detail', user_id=user.id)
    else:
        return redirect('adminpanel:user_management')


@login_required
@user_passes_test(is_admin)
@require_POST
def unblock_user(request, user_id):
    """Unblock user (set is_active=True)"""
    user = get_object_or_404(User, id=user_id)
    
    # Unblock the user
    user.is_active = True
    user.save()
    
    messages.success(request, f'User {user.username} has been unblocked successfully. They can now login.')
    
    # Redirect back to the referring page
    referer = request.META.get('HTTP_REFERER')
    if referer and 'user_detail' in referer:
        return redirect('adminpanel:user_detail', user_id=user.id)
    else:
        return redirect('adminpanel:user_management')


# ============================================================================
# BLOG MANAGEMENT VIEWS
# ============================================================================

@login_required
@user_passes_test(is_admin)
def blog_management(request):
    """Blog management page"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    category_filter = request.GET.get('category', 'all')
    
    # Base queryset
    blogs = BlogPost.objects.all().select_related('author', 'category').order_by('-created_at')
    
    # Apply search filter
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter != 'all':
        blogs = blogs.filter(status=status_filter)
    
    # Apply category filter
    if category_filter != 'all':
        blogs = blogs.filter(category_id=category_filter)
    
    # Pagination
    paginator = Paginator(blogs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter dropdown
    categories = Category.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'categories': categories,
        'total_blogs': blogs.count(),
    }
    return render(request, 'adminpanel/blog_management.html', context)


@login_required
@user_passes_test(is_admin)
def create_blog(request):
    """Create new blog post"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        excerpt = request.POST.get('excerpt', '')
        category_id = request.POST.get('category')
        status = request.POST.get('status', 'draft')
        is_featured = request.POST.get('is_featured') == 'on'
        featured_image = request.FILES.get('featured_image')
        
        # Validation
        if not title or not content:
            messages.error(request, 'Title and content are required.')
            return render(request, 'adminpanel/create_blog.html', {
                'categories': Category.objects.all().order_by('name')
            })
        
        try:
            # Create blog post
            blog = BlogPost.objects.create(
                title=title,
                content=content,
                excerpt=excerpt,
                author=request.user,
                category_id=category_id if category_id else None,
                status=status,
                is_featured=is_featured,
                featured_image=featured_image
            )
            
            # Handle attachments
            attachments = request.FILES.getlist('attachments')
            for attachment in attachments:
                BlogPostAttachment.objects.create(
                    post=blog,
                    file=attachment,
                    title=attachment.name
                )
            
            messages.success(request, f'Blog post "{title}" created successfully!')
            return redirect('adminpanel:blog_detail', blog_id=blog.id)
        except Exception as e:
            messages.error(request, f'Error creating blog post: {str(e)}')
    
    categories = Category.objects.all().order_by('name')
    return render(request, 'adminpanel/create_blog.html', {'categories': categories})


@login_required
@user_passes_test(is_admin)
def blog_detail(request, blog_id):
    """Blog detail view"""
    blog = get_object_or_404(BlogPost, id=blog_id)
    attachments = blog.attachments.all()
    comments = blog.comments.all().select_related('author').order_by('-created_at')
    
    context = {
        'blog': blog,
        'attachments': attachments,
        'comments': comments,
    }
    return render(request, 'adminpanel/blog_detail.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def approve_comment(request, blog_id, comment_id):
    """Approve a pending/rejected comment"""
    blog = get_object_or_404(BlogPost, id=blog_id)
    comment = get_object_or_404(Comment, id=comment_id, post=blog)
    comment.status = 'approved'
    comment.save(update_fields=['status'])
    messages.success(request, 'Comment approved.')
    return redirect('adminpanel:blog_detail', blog_id=blog.id)


@login_required
@user_passes_test(is_admin)
@require_POST
def reject_comment(request, blog_id, comment_id):
    """Reject a pending/approved comment"""
    blog = get_object_or_404(BlogPost, id=blog_id)
    comment = get_object_or_404(Comment, id=comment_id, post=blog)
    comment.status = 'rejected'
    comment.save(update_fields=['status'])
    messages.success(request, 'Comment rejected.')
    return redirect('adminpanel:blog_detail', blog_id=blog.id)


@login_required
@user_passes_test(is_admin)
def comment_management(request):
    """Comment management page"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    post_filter = request.GET.get('post', 'all')
    
    # Base queryset
    comments = Comment.objects.all().select_related('author', 'post').order_by('-created_at')
    
    # Apply search filter
    if search_query:
        comments = comments.filter(
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(post__title__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter != 'all':
        comments = comments.filter(status=status_filter)
    
    # Apply post filter
    if post_filter != 'all':
        comments = comments.filter(post_id=post_filter)
    
    # Pagination
    paginator = Paginator(comments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get blog posts for filter dropdown
    blog_posts = BlogPost.objects.all().order_by('-created_at')[:50]  # Recent 50 posts
    
    # Get comment statistics
    total_comments = Comment.objects.count()
    pending_comments = Comment.objects.filter(status='pending').count()
    approved_comments = Comment.objects.filter(status='approved').count()
    rejected_comments = Comment.objects.filter(status='rejected').count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'post_filter': post_filter,
        'blog_posts': blog_posts,
        'total_comments': total_comments,
        'pending_comments': pending_comments,
        'approved_comments': approved_comments,
        'rejected_comments': rejected_comments,
        'filtered_count': comments.count(),
    }
    return render(request, 'adminpanel/comment_management.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def bulk_approve_comments(request):
    """Bulk approve selected comments"""
    comment_ids = request.POST.getlist('comment_ids')
    if comment_ids:
        updated = Comment.objects.filter(id__in=comment_ids).update(status='approved')
        messages.success(request, f'{updated} comments approved successfully.')
    else:
        messages.warning(request, 'No comments selected.')
    return redirect('adminpanel:comment_management')


@login_required
@user_passes_test(is_admin)
@require_POST
def bulk_reject_comments(request):
    """Bulk reject selected comments"""
    comment_ids = request.POST.getlist('comment_ids')
    if comment_ids:
        updated = Comment.objects.filter(id__in=comment_ids).update(status='rejected')
        messages.success(request, f'{updated} comments rejected successfully.')
    else:
        messages.warning(request, 'No comments selected.')
    return redirect('adminpanel:comment_management')


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_comment(request, comment_id):
    """Delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    post_title = comment.post.title
    author = comment.author.username
    comment.delete()
    messages.success(request, f'Comment by {author} on "{post_title}" has been deleted.')
    
    # Redirect back to comment management or blog detail based on referer
    referer = request.META.get('HTTP_REFERER')
    if referer and 'comment_management' in referer:
        return redirect('adminpanel:comment_management')
    else:
        return redirect('adminpanel:blog_detail', blog_id=comment.post.id)


@login_required
@user_passes_test(is_admin)
def edit_blog(request, blog_id):
    """Edit blog post"""
    blog = get_object_or_404(BlogPost, id=blog_id)
    
    if request.method == 'POST':
        blog.title = request.POST.get('title', blog.title)
        blog.content = request.POST.get('content', blog.content)
        blog.excerpt = request.POST.get('excerpt', blog.excerpt)
        
        category_id = request.POST.get('category')
        blog.category_id = category_id if category_id else None
        
        blog.status = request.POST.get('status', blog.status)
        blog.is_featured = request.POST.get('is_featured') == 'on'
        
        # Handle featured image
        if request.FILES.get('featured_image'):
            blog.featured_image = request.FILES.get('featured_image')
        
        try:
            blog.save()
            
            # Handle new attachments
            attachments = request.FILES.getlist('attachments')
            for attachment in attachments:
                BlogPostAttachment.objects.create(
                    post=blog,
                    file=attachment,
                    title=attachment.name
                )
            
            messages.success(request, f'Blog post "{blog.title}" updated successfully!')
            return redirect('adminpanel:blog_detail', blog_id=blog.id)
        except Exception as e:
            messages.error(request, f'Error updating blog post: {str(e)}')
    
    categories = Category.objects.all().order_by('name')
    context = {
        'blog': blog,
        'categories': categories,
        'attachments': blog.attachments.all(),
    }
    return render(request, 'adminpanel/edit_blog.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_blog(request, blog_id):
    """Delete blog post"""
    blog = get_object_or_404(BlogPost, id=blog_id)
    title = blog.title
    blog.delete()
    messages.success(request, f'Blog post "{title}" has been deleted successfully.')
    return redirect('adminpanel:blog_management')


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_attachment(request, blog_id, attachment_id):
    """Delete blog attachment"""
    blog = get_object_or_404(BlogPost, id=blog_id)
    attachment = get_object_or_404(BlogPostAttachment, id=attachment_id, post=blog)
    attachment.delete()
    messages.success(request, 'Attachment deleted successfully.')
    return redirect('adminpanel:edit_blog', blog_id=blog.id)


# ============================================================================
# CATEGORY MANAGEMENT VIEWS
# ============================================================================

@login_required
@user_passes_test(is_admin)
def category_management(request):
    """Category management page"""
    search_query = request.GET.get('search', '')
    
    categories = Category.objects.all().order_by('name')
    
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Add post count for each category
    for category in categories:
        category.post_count = category.posts.count()
    
    context = {
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'adminpanel/category_management.html', context)


@login_required
@user_passes_test(is_admin)
def create_category(request):
    """Create new category"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if not name:
            messages.error(request, 'Category name is required.')
            return render(request, 'adminpanel/create_category.html')
        
        if Category.objects.filter(name=name).exists():
            messages.error(request, 'Category with this name already exists.')
            return render(request, 'adminpanel/create_category.html')
        
        try:
            category = Category.objects.create(
                name=name,
                description=description
            )
            messages.success(request, f'Category "{name}" created successfully!')
            return redirect('adminpanel:category_management')
        except Exception as e:
            messages.error(request, f'Error creating category: {str(e)}')
    
    return render(request, 'adminpanel/create_category.html')


@login_required
@user_passes_test(is_admin)
def edit_category(request, category_id):
    """Edit category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', category.name)
        description = request.POST.get('description', category.description)
        
        if not name:
            messages.error(request, 'Category name is required.')
            return render(request, 'adminpanel/edit_category.html', {'category': category})
        
        if Category.objects.filter(name=name).exclude(id=category.id).exists():
            messages.error(request, 'Category with this name already exists.')
            return render(request, 'adminpanel/edit_category.html', {'category': category})
        
        try:
            category.name = name
            category.description = description
            category.save()
            messages.success(request, f'Category "{name}" updated successfully!')
            return redirect('adminpanel:category_management')
        except Exception as e:
            messages.error(request, f'Error updating category: {str(e)}')
    
    return render(request, 'adminpanel/edit_category.html', {'category': category})


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_category(request, category_id):
    """Delete category"""
    category = get_object_or_404(Category, id=category_id)
    
    # Check if category has posts
    if category.posts.exists():
        messages.error(request, f'Cannot delete category "{category.name}" because it has associated blog posts.')
        return redirect('adminpanel:category_management')
    
    name = category.name
    category.delete()
    messages.success(request, f'Category "{name}" has been deleted successfully.')
    return redirect('adminpanel:category_management')