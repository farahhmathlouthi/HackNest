from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('login_user/', views.login_user, name='login_user'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('create_hackaton/', views.create_hackaton, name='create_hackaton'),
    path('request_organizer/', views.request_organizer, name= 'request_organizer'),
    path('hackathon/<int:hackathon_id>/', views.hackathon_details, name='hackathon_details'),  # Hackathon details
    path('hackathon/<int:hackathon_id>/register/', views.register_for_hackathon, name='register_for_hackathon'),  # Register for hackathon
]