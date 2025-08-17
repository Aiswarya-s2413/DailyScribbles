from django.contrib import admin
from .models import Category, BlogPost, BlogPostAttachment, Comment, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


class BlogPostAttachmentInline(admin.TabularInline):
    model = BlogPostAttachment
    extra = 1


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'view_count', 'like_count', 'created_at']
    list_filter = ['status', 'is_featured', 'category', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    inlines = [BlogPostAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('content', 'excerpt', 'featured_image')
        }),
        ('Publication', {
            'fields': ('status', 'is_featured')
        }),
        ('Metrics', {
            'fields': ('view_count', 'like_count'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['view_count', 'like_count']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'status', 'content_preview', 'created_at']
    list_filter = ['status', 'created_at', 'post']
    search_fields = ['content', 'author__username', 'post__title']
    actions = ['approve_comments', 'reject_comments']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def approve_comments(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} comments approved.")
    approve_comments.short_description = "Approve selected comments"
    
    def reject_comments(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} comments rejected.")
    reject_comments.short_description = "Reject selected comments"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at', 'post']
    search_fields = ['user__username', 'post__title']
