from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DeleteView, DetailView, UpdateView, View, TemplateView
from django.http import HttpResponse
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm, ContactForm, UserUpdateForm, ProfileUpdateForm
from .models import Post, Like, Service, Portfolio, Profile




# Profile view
class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'registration/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Make sure user has a profile
        Profile.objects.get_or_create(user=self.request.user)
        
        # Get all posts by this user, ordered by creation date (newest first)
        context['user_posts'] = Post.objects.filter(author=self.request.user).order_by('-created_at')
        
        return context

# class ProfileView(LoginRequiredMixin, TemplateView):
#     template_name = 'registration/profile.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = self.request.user
#         # Get filter parameters
#         portfolio_type = self.request.GET.get('type', '')
#         status = self.request.GET.get('status', '')

#         # Show all portfolio items (no user filter)
#         portfolio_items = Portfolio.objects.all()
#         if portfolio_type:
#             portfolio_items = portfolio_items.filter(portfolio_type=portfolio_type)
#         if status:
#             portfolio_items = portfolio_items.filter(status=status)

#         featured_items = portfolio_items.filter(is_featured=True)

#         portfolio_stats = {
#             'total_projects': portfolio_items.count(),
#             'completed_projects': portfolio_items.filter(status='completed').count(),
#             'in_progress_projects': portfolio_items.filter(status='in_progress').count(),
#             'technologies_used': len(set([tech.strip() for item in portfolio_items for tech in item.get_technologies_list()])),
#         }

#         available_types = portfolio_items.values_list('portfolio_type', flat=True).distinct()
#         available_statuses = portfolio_items.values_list('status', flat=True).distinct()

#         context.update({
#             'user': user,
#             'portfolio_items': portfolio_items,
#             'featured_items': featured_items,
#             'portfolio_stats': portfolio_stats,
#             'available_types': available_types,
#             'available_statuses': available_statuses,
#             'current_type_filter': portfolio_type,
#             'current_status_filter': status,
#             'portfolio_type_choices': Portfolio.PORTFOLIO_TYPES,
#             'status_choices': Portfolio.STATUS_CHOICES,
#         })
#         return context
    

class ProfileDetailView(DetailView):
    model = User
    template_name = 'core/profile_detail.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related posts
        context['posts'] = self.object.post_set.all()
        return context


# Profile update view
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'core/profile_update.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        # Create profile if it doesn't exist
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Expose the profile form as p_form for the template (alias to default 'form')
        context['p_form'] = context.get('form')
        if self.request.POST:
            context['u_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['u_form'] = UserUpdateForm(instance=self.request.user)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        u_form = context['u_form']
        
        if u_form.is_valid():
            u_form.save()
            messages.success(self.request, 'Your profile has been updated!')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
        
        

# Home view
class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = Post.objects.order_by('-created_at')[:3]  # Show top 3 posts
        return context


# Signup view
class UserResgisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')




class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm  # or fields = ['title', 'content', 'image', ...]
    template_name = 'core/post_create.html'
    success_url = reverse_lazy('all posts')
    
    def form_valid(self, form):
        # Assign the current user as the author before saving
        form.instance.author = self.request.user
        return super().form_valid(form)
    
# view for listing all posts
class PostListView(ListView):
    model = Post
    template_name = 'core/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at'] # Newest first



# View post details
class PostDetailView(DetailView):
    model = Post
    template_name = 'core/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['form'] = CommentForm()
        user = self.request.user
        liked_by_user = False
        if user.is_authenticated:
            liked_by_user = post.likes.filter(user=user).exists()
        context['liked_by_user'] = liked_by_user
        return context

# View for editing Posts
class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'core/post_edit.html'
    success_url = reverse_lazy('all posts')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
class PostEditPartialView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = PostForm(instance=post)
        context = {'form': form, 'post': post}
        html = render_to_string('core/partials/post_edit_form.html', context, request)
        return HttpResponse(html)

    def test_func(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return self.request.user == post.author

    

    

class PostEditSubmitView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            # Return updated detail HTML to replace the form
            return render(request, 'core/post_detail.html', {'post': post})
        else:
            # Return form again with errors
            return render(request, 'core/partials/post_edit_form.html', {'form': form, 'post': post})

    def test_func(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return self.request.user == post.author

    


# View for handling delete of a particular post
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'core/post_delete.html'
    success_url = reverse_lazy('all posts')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
# View for handling likes
class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()  # unlike
        html = render_to_string('core/partials/like_button.html', {'post': post, 'user': request.user})
        return HttpResponse(html)
    

@method_decorator(login_required, name='dispatch')
class AddCommentView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post detail', pk=pk)
        context = {
            'post': post,
            'form': form,
        }
        return render(request, 'core/post_detail.html', context)


class ServicesPageView(ListView):
    model = Service
    template_name = 'core/services.html'
    context_object_name = 'services'



# About page view with portfolio items

class AboutView(TemplateView):
    """About page view with portfolio items"""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        portfolio_type = self.request.GET.get('type', '')
        status = self.request.GET.get('status', '')
        
        # Base queryset - only public items
        portfolio_items = Portfolio.objects.filter(is_public=True)
        
        # Apply filters
        if portfolio_type:
            portfolio_items = portfolio_items.filter(portfolio_type=portfolio_type)
        if status:
            portfolio_items = portfolio_items.filter(status=status)
        
        # Get featured items
        featured_items = portfolio_items.filter(is_featured=True)
        
        # Get portfolio statistics
        portfolio_stats = {
            'total_projects': Portfolio.objects.filter(is_public=True).count(),
            'completed_projects': Portfolio.objects.filter(is_public=True, status='completed').count(),
            'in_progress_projects': Portfolio.objects.filter(is_public=True, status='in_progress').count(),
            'technologies_used': len(set([tech.strip() for item in Portfolio.objects.filter(is_public=True) for tech in item.get_technologies_list()])),
        }
        
        # Get unique portfolio types and statuses for filters
        available_types = Portfolio.objects.filter(is_public=True).values_list('portfolio_type', flat=True).distinct()
        available_statuses = Portfolio.objects.filter(is_public=True).values_list('status', flat=True).distinct()
        
        context.update({
            'portfolio_items': portfolio_items,
            'featured_items': featured_items,
            'portfolio_stats': portfolio_stats,
            'available_types': available_types,
            'available_statuses': available_statuses,
            'current_type_filter': portfolio_type,
            'current_status_filter': status,
            'portfolio_type_choices': Portfolio.PORTFOLIO_TYPES,
            'status_choices': Portfolio.STATUS_CHOICES,
        })
        
        return context


# Portfolio detail view
class PortfolioDetailView(DetailView):
    """Individual portfolio item detail view"""
    model = Portfolio
    template_name = 'portfolio_detail.html'
    context_object_name = 'portfolio_item'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Portfolio.objects.filter(is_public=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get related projects (same type, excluding current)
        related_projects = Portfolio.objects.filter(
            portfolio_type=self.object.portfolio_type,
            is_public=True
        ).exclude(id=self.object.id)[:3]
        
        context['related_projects'] = related_projects
        return context


# Contact View
class ContactView(TemplateView):
    """Contact page with form handling"""
    template_name = 'core/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        
        # Contact information
        contact_info = {
            'address': 'bamenda, Northwest, Cameroon',  
            'phone_primary': '+237 674658654',
            'phone_secondary': '+237 696831084',
            'email': 'loickemloung@gmail.com',
            'business_hours': {
                'weekdays': 'Monday - Friday: 8:00 AM - 6:00 PM',
                'weekends': 'Saturday - Sunday: 10:00 AM - 4:00 PM'
            },
            'social_media': {
                'linkedin': 'https://www.linkedin.com/in/kemloung-loic-cabrel-2585202b4/',
                'twitter': 'https://x.com/kemloungloic',
                'github': 'https://github.com/Cabrel-loic',
                'instagram': 'https://www.instagram.com/kemloungcabrel/'
            }
        }
        
        context['contact_info'] = contact_info
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # Save the message
            contact_message = form.save()
            
            # Send notification email (optional)
            try:
                self.send_notification_email(contact_message)
            except Exception as e:
                print(f"Failed to send email notification: {e}")
            
            # Send confirmation message
            messages.success(
                request, 
                f"Thank you {contact_message.name}! Your message has been sent successfully. "
                "I'll get back to you as soon as possible."
            )
            
            return redirect('contact')
        
        else:
            messages.error(
                request, 
                "There was an error with your submission. Please check the form and try again."
            )
        
        # If form is invalid, render with errors
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    
    def send_notification_email(self, contact_message):
        """Send email notification when new message is received"""
        subject = f"New Contact Message from {contact_message.name}"
        message = f"""
        New contact message received from CabrelBlog:
        
        Name: {contact_message.name}
        Email: {contact_message.email}
        Phone: {contact_message.phone or 'Not provided'}
        Subject: {contact_message.subject}
        
        Message:
        {contact_message.message}
        
        ---
        Sent from CabrelBlog Contact Form
        """
        
        # Send to your email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],  # Add ADMIN_EMAIL to your settings
            fail_silently=False,
        )