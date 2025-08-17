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
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
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