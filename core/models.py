from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os
# from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return str(self.name)
    

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return str(self.name)
    

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, blank = True)
    tags = models.ManyToManyField(Tag, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'created_at'


    def __str__(self):
        return str(self.title)
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'


# Like model
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = ('post', 'user') #prevents multiple likes

    def __str__(self):
        return f'{self.user.username} liked {self.post.title}'
    

class Service(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, help_text="Emoji or icon code (e.g. 💻, ☁️, 🧠)")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return str(self.title)




# Portfolio model

class Portfolio(models.Model):
    PORTFOLIO_TYPES = [
        ('web_app', 'Web Application'),
        ('mobile_app', 'Mobile Application'),
        ('api', 'API/Backend Service'),
        ('website', 'Website'),
        ('design', 'Design Work'),
        ('data_analysis', 'Data Analysis'),
        ('machine_learning', 'Machine Learning'),
        ('game', 'Game Development'),
        ('desktop_app', 'Desktop Application'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('archived', 'Archived'),
        ('concept', 'Concept/Planning'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, help_text="URL-friendly version of title")
    portfolio_type = models.CharField(max_length=20, choices=PORTFOLIO_TYPES, default='web_app')
    short_description = models.CharField(max_length=300, help_text="Brief description for cards")
    bio = models.TextField(help_text="Detailed description")
    
    # Images
    featured_image = models.ImageField(upload_to='portfolio/featured/', blank=True, null=True)
    gallery_images = models.TextField(blank=True, help_text="Comma-separated image URLs or paths")
    
    # Links
    live_url = models.URLField(blank=True, null=True, help_text="Live project URL")
    github_url = models.URLField(blank=True, null=True, help_text="GitHub repository URL")
    demo_url = models.URLField(blank=True, null=True, help_text="Demo/Preview URL")
    documentation_url = models.URLField(blank=True, null=True, help_text="Documentation URL")
    
    # Technical details
    technologies = models.CharField(max_length=500, help_text="Comma-separated technologies")
    key_features = models.TextField(blank=True, help_text="Key features (one per line)")
    challenges = models.TextField(blank=True, help_text="Technical challenges overcome")
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., '3 months', '2 weeks'")
    
    # Organization
    is_featured = models.BooleanField(default=False, help_text="Feature this project")
    is_public = models.BooleanField(default=True, help_text="Show publicly")
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']
        verbose_name_plural = "Portfolio Items"

    def __str__(self):
        return f"{self.title} ({self.get_portfolio_type_display()})"

    def get_technologies_list(self):
        """Return technologies as a list"""
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
    
    def get_key_features_list(self):
        """Return key features as a list"""
        if not self.key_features:
            return []
        return [feature.strip() for feature in self.key_features.split('\n') if feature.strip()]
    
    def get_gallery_images_list(self):
        """Return gallery images as a list"""
        if not self.gallery_images:
            return []
        return [img.strip() for img in self.gallery_images.split(',') if img.strip()]
    
    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'completed': 'bg-green-100 text-green-800',
            'in_progress': 'bg-blue-100 text-blue-800',
            'archived': 'bg-gray-100 text-gray-800',
            'concept': 'bg-yellow-100 text-yellow-800',
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Portfolio.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
    def get_type_icon(self):
        """Return icon class based on portfolio type"""
        type_icons = {
            'web_app': '🌐',
            'mobile_app': '📱',
            'api': '⚙️',
            'website': '🖥️',
            'design': '🎨',
            'data_analysis': '📊',
            'machine_learning': '🤖',
            'game': '🎮',
            'desktop_app': '💻',
            'other': '📋',
        }
        return type_icons.get(self.portfolio_type, '📋')

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Portfolio.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


# Contact page model

class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'new': 'bg-blue-100 text-blue-800',
            'read': 'bg-yellow-100 text-yellow-800',
            'replied': 'bg-green-100 text-green-800',
            'archived': 'bg-gray-100 text-gray-800',
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')
    


# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    
    # Contact Details
    phone = models.CharField(max_length=20, blank=True, help_text="Your phone number")
    website = models.URLField(max_length=200, blank=True, help_text="Your personal website or portfolio")
    location = models.CharField(max_length=100, blank=True, help_text="City, Country")
    twitter = models.CharField(max_length=50, blank=True, help_text="Twitter username (without @)")
    linkedin = models.URLField(max_length=200, blank=True, help_text="LinkedIn profile URL")
    github = models.CharField(max_length=50, blank=True, help_text="GitHub username")
    
    # Additional Info
    date_of_birth = models.DateField(null=True, blank=True)
    profession = models.CharField(max_length=100, blank=True, help_text="Your job title or profession")
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image to save space (only if image exists)
        if self.image and os.path.exists(self.image.path):
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

# Create profile automatically when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)