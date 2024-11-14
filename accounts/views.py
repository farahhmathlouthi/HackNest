from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib import messages
from django.contrib.auth import logout

def signup(request):
    form = SignUpForm()
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login_user(request)
                return redirect('home')
            else:
                print("Authentication failed")
                return redirect('signup')
    else:
        print(form.errors)    
    return render(request, 'accounts/signup.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def home(request):
    return render(request, 'accounts/home.html')

def welcome(request):
    return render(request, 'accounts/welcome.html')

def logout_view(request):
    logout(request)
    return render(request, 'accounts/welcome.html')