from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_exercise, name='add_exercise'),
    path('edit/<int:pk>/', views.edit_exercise, name='edit_exercise'),
    path('delete/<int:pk>/', views.delete_exercise, name='delete_exercise'),
    path('signup/', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/create/', views.create_profile, name='create_profile'),

]
