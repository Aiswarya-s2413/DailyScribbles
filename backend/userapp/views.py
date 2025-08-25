from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json

User = get_user_model()


# Frontend Template Views
def login_page(request):
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(username=username)
            if not user_obj.is_active:
                messages.error(request, 'Your account has been blocked. Please contact the administrator.')
                return render(request, 'userapp/login.html')
        except User.DoesNotExist:
            pass
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            next_url = request.GET.get('next', 'blog:post_list')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'userapp/login.html')


def register_page(request):
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password1 = request.POST.get('password1') or ''
        password2 = request.POST.get('password2') or ''
        first_name = (request.POST.get('first_name', '') or '').strip()
        last_name = (request.POST.get('last_name', '') or '').strip()

        def only_spaces_or_symbols(s: str) -> bool:
            if not s or not s.strip():
                return True
            return all(not ch.isalnum() for ch in s.strip())

        def only_numbers(s: str) -> bool:
            s = s.strip()
            return len(s) > 0 and s.isdigit()

        if only_spaces_or_symbols(username):
            messages.error(request, 'Username cannot be empty, spaces-only, or symbols-only.')
            return render(request, 'userapp/register.html')
        if only_spaces_or_symbols(first_name):
            messages.error(request, 'First name cannot be empty, spaces-only, or symbols-only.')
            return render(request, 'userapp/register.html')
        if only_spaces_or_symbols(last_name):
            messages.error(request, 'Last name cannot be empty, spaces-only, or symbols-only.')
            return render(request, 'userapp/register.html')

        if only_numbers(username):
            messages.error(request, 'Username cannot be numbers only.')
            return render(request, 'userapp/register.html')
        if only_numbers(first_name):
            messages.error(request, 'First name cannot be numbers only.')
            return render(request, 'userapp/register.html')
        if only_numbers(last_name):
            messages.error(request, 'Last name cannot be numbers only.')
            return render(request, 'userapp/register.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'userapp/register.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'userapp/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'userapp/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'userapp/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'userapp/register.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('userapp:login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'userapp/register.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('blog:post_list')





# Simple JSON API Endpoints
@csrf_exempt
@require_POST
def api_login(request):
    """API login endpoint"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)
        
        # Check if user exists and is blocked
        try:
            user_obj = User.objects.get(username=username)
            if not user_obj.is_active:
                return JsonResponse({'error': 'Your account has been blocked. Please contact the administrator.'}, status=403)
        except User.DoesNotExist:
            pass
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_register(request):
    try:
        data = json.loads(request.body)
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip()
        password = (data.get('password') or '')
        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()
        
        # Inline validation: block spaces-only, symbols-only, and numbers-only where applicable
        def only_spaces_or_symbols(s: str) -> bool:
            if not s or not s.strip():
                return True
            return all(not ch.isalnum() for ch in s.strip())
        
        def only_numbers(s: str) -> bool:
            s = s.strip()
            return len(s) > 0 and s.isdigit()
        
        if only_spaces_or_symbols(username):
            return JsonResponse({'error': 'Username cannot be empty, spaces-only, or symbols-only'}, status=400)
        if only_spaces_or_symbols(first_name):
            return JsonResponse({'error': 'First name cannot be empty, spaces-only, or symbols-only'}, status=400)
        if only_spaces_or_symbols(last_name):
            return JsonResponse({'error': 'Last name cannot be empty, spaces-only, or symbols-only'}, status=400)
        if only_numbers(username):
            return JsonResponse({'error': 'Username cannot be numbers only'}, status=400)
        if only_numbers(first_name):
            return JsonResponse({'error': 'First name cannot be numbers only'}, status=400)
        if only_numbers(last_name):
            return JsonResponse({'error': 'Last name cannot be numbers only'}, status=400)
        
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'error': 'Please enter a valid email address'}, status=400)
        
        if not password or len(password) < 8:
            return JsonResponse({'error': 'Password must be at least 8 characters long'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def api_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({'success': True, 'message': 'Logout successful'})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

