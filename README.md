# 📝 DailyScribbles

A modern, feature-rich blogging platform built with Django that combines powerful content management with a beautiful user experience. DailyScribbles offers both a public blog interface and a comprehensive admin panel for content creators.

![Django](https://img.shields.io/badge/Django-5.2.5-green.svg)
![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)
![AWS S3](https://img.shields.io/badge/AWS-S3-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple.svg)

## ✨ Features

### 🎯 Core Features
- **Modern Blog Platform**: Clean, responsive design for optimal reading experience
- **Rich Content Management**: Create, edit, and manage blog posts with featured images and attachments
- **Category System**: Organize content with hierarchical categories
- **User Authentication**: Secure JWT-based authentication system
- **Comment System**: Threaded comments with moderation capabilities
- **Engagement Metrics**: Track views, likes, and user interactions

### 🛡️ Admin Panel
- **Comprehensive Dashboard**: Overview of all blog statistics and recent activity
- **Content Management**: Full CRUD operations for posts, categories, and users
- **Comment Moderation**: Approve, reject, or manage user comments
- **User Management**: Admin tools for user accounts and permissions
- **Media Management**: Handle file uploads and attachments

### 🚀 Technical Features
- **RESTful API**: Complete API endpoints for all functionality
- **Cloud Storage**: AWS S3 integration for scalable media storage
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **SEO Optimized**: Clean URLs, meta tags, and search engine friendly
- **Performance**: Optimized queries and caching strategies

## 🏗️ Architecture

```
DailyScribbles/
├── backend/                 # Django backend application
│   ├── backend/            # Main project settings
│   ├── blog/               # Blog app (models, views, APIs)
│   ├── userapp/            # User management and authentication
│   ├── adminpanel/         # Admin interface and management
│   ├── templates/          # HTML templates
│   ├── static/             # Static files (CSS, JS, images)
│   ├── media/              # User uploaded files
│   └── manage.py           # Django management script
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## 🛠️ Technology Stack

### Backend
- **Django 5.2.5**: Web framework
- **Django REST Framework**: API development
- **SQLite**: Database (easily configurable for PostgreSQL/MySQL)
- **JWT Authentication**: Secure token-based auth
- **Pillow**: Image processing
- **django-storages**: Cloud storage integration

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icon library
- **Vanilla JavaScript**: Interactive components
- **HTML5/CSS3**: Modern web standards

### Cloud & Storage
- **AWS S3**: Media file storage
- **boto3**: AWS SDK for Python

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/DailyScribbles.git
   cd DailyScribbles
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   
   Create a `.env` file in the `backend/` directory:
   ```env
   # AWS S3 Configuration (Optional - set USE_S3=False for local storage)
   USE_S3=False
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_STORAGE_BUCKET_NAME=your_bucket_name
   AWS_S3_REGION_NAME=your_region
   
   # Django Settings
   DEBUG=True
   SECRET_KEY=your_secret_key_here
   ```

5. **Database Setup**
   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   - **Blog**: http://127.0.0.1:8000/
   - **Admin Panel**: http://127.0.0.1:8000/adminpanel/
   - **Django Admin**: http://127.0.0.1:8000/admin/
   - **API Documentation**: http://127.0.0.1:8000/api/

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/` - Get JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Blog Posts
- `GET /api/blog/posts/` - List all published posts
- `GET /api/blog/posts/{id}/` - Get specific post
- `POST /api/blog/posts/` - Create new post (authenticated)
- `PUT /api/blog/posts/{id}/` - Update post (author only)
- `DELETE /api/blog/posts/{id}/` - Delete post (author only)

### Categories
- `GET /api/blog/categories/` - List all categories
- `GET /api/blog/categories/{id}/posts/` - Get posts by category

### Comments
- `GET /api/blog/posts/{id}/comments/` - Get post comments
- `POST /api/blog/posts/{id}/comments/` - Add comment (authenticated)

### Likes
- `POST /api/blog/posts/{id}/like/` - Toggle like (authenticated)

## 🎨 Features in Detail

### Blog Management
- **Rich Text Editor**: Create engaging content with formatting options
- **Featured Images**: Eye-catching visuals for each post
- **File Attachments**: Support for documents, images, and other files
- **Draft System**: Save and preview posts before publishing
- **SEO-Friendly URLs**: Automatic slug generation from titles

### User Experience
- **Responsive Design**: Seamless experience across all devices
- **Fast Loading**: Optimized images and efficient queries
- **Search Functionality**: Find content quickly and easily
- **Social Features**: Like and comment on posts

### Admin Features
- **Dashboard Analytics**: Track blog performance and engagement
- **Content Moderation**: Review and approve user-generated content
- **User Management**: Handle user accounts and permissions
- **Bulk Operations**: Efficiently manage multiple items

## 🔧 Configuration

### Storage Configuration
The application supports both local and AWS S3 storage:

**Local Storage (Development)**
```python
USE_S3 = False
```

**AWS S3 Storage (Production)**
```python
USE_S3 = True
AWS_ACCESS_KEY_ID = 'your_key'
AWS_SECRET_ACCESS_KEY = 'your_secret'
AWS_STORAGE_BUCKET_NAME = 'your_bucket'
```

### Database Configuration
Default SQLite configuration for development. For production, update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG = False` in settings
- [ ] Configure production database
- [ ] Set up AWS S3 for media files
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up SSL/HTTPS
- [ ] Configure static file serving
- [ ] Set up monitoring and logging

### Environment Variables
```env
DEBUG=False
SECRET_KEY=your_production_secret_key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=your_database_url
USE_S3=True
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the responsive UI components
- Font Awesome for the beautiful icons
- AWS for reliable cloud storage solutions

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/DailyScribbles/issues) page
2. Create a new issue with detailed information
3. Contact the maintainers

## 🔮 Roadmap

- [ ] **Search Functionality**: Full-text search across posts
- [ ] **Email Notifications**: Comment and post notifications
- [ ] **Social Media Integration**: Share posts on social platforms
- [ ] **Multi-language Support**: Internationalization
- [ ] **Advanced Analytics**: Detailed engagement metrics
- [ ] **Mobile App**: React Native companion app
- [ ] **Newsletter System**: Email subscriptions
- [ ] **Advanced Editor**: WYSIWYG editor with more features

---

**Made with ❤️ by [Your Name]**

*DailyScribbles - Where every thought becomes a story*