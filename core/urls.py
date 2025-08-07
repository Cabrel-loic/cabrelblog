from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name = 'home'),

    path('register/', views.UserResgisterView.as_view(), name = 'register'),
    path('accounts/profile/', views.ProfileView.as_view(), name='profile'),

    path('posts/', views.PostListView.as_view(), name= 'all posts'),
    path('post/new/', views.PostCreateView.as_view(), name='create post'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name = 'post detail'),
    path('post/<int:pk>/edit/', views.PostEditView.as_view(), name='edit post'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete post'),

    path('post/<int:pk>/edit-inline', views.PostEditPartialView.as_view(), name='post edit partial'),
    path('post/<int:pk>/edit-submit',views.PostEditSubmitView.as_view(), name='post edit submit'),
    
    path('post<int:pk>/like', views.ToggleLikeView.as_view() , name = 'like'),
    path('post/<int:pk>/comment/',views.AddCommentView.as_view(), name='add_comment'),

    # Srvices page
    path('services/', views.ServicesPageView.as_view(), name='services'),

    # About page
    path('about/', views.AboutView.as_view(), name='about'),

    # Contact page
    path('contact/', views.ContactView.as_view(), name='contact'),

]
