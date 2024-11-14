from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('login_user/', views.login_user, name='login_user'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]