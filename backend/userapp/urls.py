from django.urls import path, include
from . import views

app_name = 'userapp'

# API URLs
api_urlpatterns = [
    path('login/', views.api_login, name='api-login'),
    path('register/', views.api_register, name='api-register'),
    path('logout/', views.api_logout, name='api-logout'),
]

# Frontend Template URLs
frontend_urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_view, name='logout'),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('', include(frontend_urlpatterns)),
]