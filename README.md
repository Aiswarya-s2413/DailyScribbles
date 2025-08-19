DailyScribbles
A Django-based blog platform with a custom admin panel, REST API, JWT authentication, categories, comments, likes, and media uploads. Supports optional AWS S3 storage for media.

Features
Custom Admin Panel: Manage posts, categories, users; moderate comments; upload attachments.
Blog: Post listing, post detail, categories, comments (threadable), likes, featured image.
REST API: Endpoints for posts, categories, and comments.
Auth: JWT (SimpleJWT) and session auth.
Media & Static: Local dev storage or AWS S3 in production.
Tech Stack
Backend: Django 5.2, DRF, SimpleJWT
Storage: Local filesystem or S3 via django-storages/boto3
DB: SQLite (default; can be swapped)
Python: 3.13 (per venv)
Project Structure
backend/
  adminpanel/            # Custom admin views & URLs
  blog/                  # Blog app: models, views, urls
  backend/               # Django project settings and root URLs
  templates/             # HTML templates (adminpanel, blog, base)
  static/                # Dev static files
  staticfiles/           # Collected static (prod)
  media/                 # Uploaded media (dev)
  manage.py
requirements.txt
Getting Started
1) Prerequisites
Python 3.13
pip
(Optional) virtualenv
2) Clone & Setup
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
3) Environment Variables
Create backend/.env (the project auto-loads this file):

# Core
DEBUG=True
USE_S3=False

# Only needed if using S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
AWS_S3_REGION_NAME=us-east-1
Notes:

SECRET_KEY is currently hardcoded in settings for dev. For production, move it into .env and reference it there.
Configure ALLOWED_HOSTS in backend/backend/settings.py for production.
4) Database & Admin
# From repository root
python backend/manage.py migrate
python backend/manage.py createsuperuser
5) Run the Development Server
python backend/manage.py runserver
App: http://127.0.0.1:8000/
Admin panel: http://127.0.0.1:8000/adminpanel/
Django admin: http://127.0.0.1:8000/admin/
URLs and Endpoints
Frontend (HTML)
Home (post list): /
Post detail: /post/<slug:slug>/
Category posts: /category/<slug:slug>/
Add comment (POST): /post/<slug:slug>/comment/
Toggle like (POST): /post/<slug:slug>/like/
Admin Panel (Custom)
Dashboard: /adminpanel/
Blog management: /adminpanel/blogs/
Create post: /adminpanel/blogs/create/
Post detail: /adminpanel/blogs/<int:blog_id>/
Edit post: /adminpanel/blogs/<int:blog_id>/edit/
Delete post: /adminpanel/blogs/<int:blog_id>/delete/
Approve/Reject comment: /adminpanel/blogs/<int:blog_id>/comments/<int:comment_id>/approve|reject/
Category management: /adminpanel/categories/
API (DRF)
Available under /api/ (and also under /api/blog/api/, due to how URLs are included).

Posts list: GET /api/posts/
Post detail: GET /api/posts/<slug:slug>/
Categories: GET /api/categories/
Add comment: POST /api/posts/<slug:slug>/comment/
JSON body: { "content": "Your comment" }
Requires authentication.
Auth (JWT)
Obtain token: POST /api/auth/token/ with { "username": "...", "password": "..." }
Refresh token: POST /api/auth/token/refresh/ with { "refresh": "..." }
DRF is configured with:

JWTAuthentication (Bearer tokens)
SessionAuthentication
Default permission: IsAuthenticated (you may need to allow anonymous access in specific views if desired)
Media & Static
Dev:
MEDIA_URL=/media/, MEDIA_ROOT=backend/media
STATIC_URL=/static/, STATICFILES_DIRS=[backend/static]
Prod:
Set USE_S3=True and provide AWS credentials to serve media from S3.
Static files are collected to backend/staticfiles via python backend/manage.py collectstatic.
Custom User
Model: userapp.CustomUser with unique email (set via AUTH_USER_MODEL).
Create users via Django admin or createsuperuser.
Running Tests
python backend/manage.py test
Deployment Notes
Set DEBUG=False and configure ALLOWED_HOSTS.
Move SECRET_KEY into backend/.env.
Configure a real database (e.g., Postgres) and update DATABASES.
Use a proper web server (gunicorn/uvicorn) and reverse proxy (nginx).
If serving media via S3, ensure USE_S3=True and AWS credentials are set.
