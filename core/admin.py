from django.contrib import admin
from .models import Category, Portfolio, Post, Tag, Comment, Like, Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    ordering = ('order',)


# @admin.register(Portfolio)
# class PortfolioAdmin(admin.ModelAdmin):
#     list_display = ('title', 'order')
#     ordering = ('order',)




admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)



# Add this to your admin.py file

from django.contrib import admin
from .models import Portfolio

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['title', 'portfolio_type', 'status', 'is_featured', 'is_public', 'order', 'created_at']
    list_filter = ['portfolio_type', 'status', 'is_featured', 'is_public', 'created_at']
    list_editable = ['is_featured', 'is_public', 'order', 'status']
    search_fields = ['title', 'short_description', 'description', 'technologies']
    ordering = ['-is_featured', 'order', '-created_at']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'portfolio_type', 'status')
        }),
        ('Content', {
            'fields': ('short_description', 'description', 'key_features', 'challenges')
        }),
        ('Media', {
            'fields': ('featured_image', 'gallery_images'),
            'classes': ('collapse',)
        }),
        ('Links', {
            'fields': ('live_url', 'github_url', 'demo_url', 'documentation_url'),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': ('technologies', 'start_date', 'end_date', 'duration'),
            'classes': ('collapse',)
        }),
        ('Organization', {
            'fields': ('is_featured', 'is_public', 'order')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    

    # Contact section
# Add this to your admin.py file

from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['name', 'email', 'subject', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message Details', {
            'fields': ('subject', 'message', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Only allow superusers to delete messages
        return request.user.is_superuser