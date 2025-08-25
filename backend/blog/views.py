from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.contrib.auth import get_user_model
import json
from .models import Category, BlogPost, BlogPostAttachment, Comment, Like

User = get_user_model()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def blog_list_view(request):
    posts = BlogPost.objects.filter(status='published').select_related('author', 'category')
    
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    featured_posts = posts.filter(is_featured=True)[:3]
    
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'featured_posts': featured_posts,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
    }
    return render(request, 'blog/post_list.html', context)


def blog_detail_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count once per session for this post
    viewed_posts = request.session.get('viewed_posts', [])
    if post.id not in viewed_posts:
        BlogPost.objects.filter(id=post.id).update(view_count=F('view_count') + 1)
        viewed_posts.append(post.id)
        request.session['viewed_posts'] = viewed_posts
    
    # Get approved comments
    comments = Comment.objects.filter(
        post=post, 
        status='approved', 
        parent=None
    ).select_related('author').prefetch_related('replies')
    
    # Check if user liked the post
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, post=post).exists()
    
    # Get related posts
    related_posts = BlogPost.objects.filter(
        category=post.category, 
        status='published'
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'comments': comments,
        'is_liked': is_liked,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)


@login_required
@require_POST
def add_comment(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    content = request.POST.get('content')
    parent_id = request.POST.get('parent_id')
    
    if content:
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)
        
        Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent=parent
        )
        messages.success(request, 'Your comment has been submitted and is awaiting approval.')
    else:
        messages.error(request, 'Comment content cannot be empty.')
    
    return redirect('blog:post_detail', slug=slug)


@login_required
@require_POST
def toggle_like(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )
    
    if created:
        # Increment like count
        BlogPost.objects.filter(id=post.id).update(like_count=F('like_count') + 1)
        liked = True
        message = 'Post liked successfully'
    else:
        # Remove like and decrement count
        like.delete()
        BlogPost.objects.filter(id=post.id).update(like_count=F('like_count') - 1)
        liked = False
        message = 'Post unliked successfully'
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': post.like_count + (1 if liked else -1),
            'message': message
        })
    
    # Redirect for regular form submissions
    messages.success(request, message)
    return redirect('blog:post_detail', slug=slug)


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(
        category=category, 
        status='published'
    ).select_related('author')
    
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category_posts.html', context)


# Simple JSON API Endpoints
def api_posts_list(request):
    posts = BlogPost.objects.filter(status='published').select_related('author', 'category')
    
    # Apply filters
    category = request.GET.get('category')
    if category:
        posts = posts.filter(category__slug=category)
    
    search = request.GET.get('search')
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search)
        )
    
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    
    paginator = Paginator(posts, per_page)
    page_obj = paginator.get_page(page)
    
    posts_data = []
    for post in page_obj:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'author': post.author.username,
            'category': post.category.name if post.category else None,
            'featured_image': post.featured_image.url if post.featured_image else None,
            'view_count': post.view_count,
            'like_count': post.like_count,
            'created_at': post.created_at.isoformat(),
        })
    
    return JsonResponse({
        'posts': posts_data,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    })


def api_post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count once per session for this post (API)
    viewed_posts = request.session.get('viewed_posts', [])
    if post.id not in viewed_posts:
        BlogPost.objects.filter(id=post.id).update(view_count=F('view_count') + 1)
        viewed_posts.append(post.id)
        request.session['viewed_posts'] = viewed_posts
    
    # Get comments
    comments = Comment.objects.filter(
        post=post, 
        status='approved', 
        parent=None
    ).select_related('author')
    
    comments_data = []
    for comment in comments:
        replies_data = []
        for reply in comment.replies.filter(status='approved'):
            replies_data.append({
                'id': reply.id,
                'author': reply.author.username,
                'content': reply.content,
                'created_at': reply.created_at.isoformat(),
            })
        
        comments_data.append({
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'replies': replies_data,
        })
    
    post_data = {
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'content': post.content,
        'excerpt': post.excerpt,
        'author': post.author.username,
        'category': post.category.name if post.category else None,
        'featured_image': post.featured_image.url if post.featured_image else None,
        'view_count': post.view_count,
        'like_count': post.like_count,
        'created_at': post.created_at.isoformat(),
        'comments': comments_data,
    }
    
    return JsonResponse(post_data)


def api_categories_list(request):
    categories = Category.objects.all()
    categories_data = []
    
    for category in categories:
        categories_data.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'description': category.description,
            'post_count': category.posts.filter(status='published').count(),
        })
    
    return JsonResponse({'categories': categories_data})


@require_POST
def api_add_comment(request, slug):
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    try:
        data = json.loads(request.body)
        content = data.get('content')
        parent_id = data.get('parent_id')
        
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)
        
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent=parent
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Comment submitted successfully',
            'comment': {
                'id': comment.id,
                'author': comment.author.username,
                'content': comment.content,
                'status': comment.status,
                'created_at': comment.created_at.isoformat(),
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
