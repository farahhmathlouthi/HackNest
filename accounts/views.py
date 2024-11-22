from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseForbidden
from .forms import SignUpForm, HackathonForm, RequestToBeOrganizerForm, RegistrationForm
from django.contrib import messages
from .models import RequestToBeOrganizer, Hackathon, Team, Registration
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail


@login_required
def request_organizer(request):
    if request.method == 'POST':
        form = RequestToBeOrganizerForm(request.POST)
        if form.is_valid():
            # Save the request with the user who is making it
            request_instance = form.save(commit=False)
            request_instance.user = request.user
            request_instance.save()
            return redirect('home')  # Redirect to a confirmation page
    else:
        form = RequestToBeOrganizerForm()

    return render(request, 'accounts/request_organizer.html', {'form': form})


@login_required
def create_hackaton(request):
    # Check if the user is an approved organizer
    try:
        user_role = RequestToBeOrganizer.objects.get(user=request.user)
        if not user_role.is_approved:
            return HttpResponseForbidden('You are not approved as an organizer yet.')
    except RequestToBeOrganizer.DoesNotExist:
        return HttpResponseForbidden('You must request to become an organizer first.')

    if request.method == 'POST':
        form = HackathonForm(request.POST, request.FILES)
        if form.is_valid():
            hackathon = form.save(commit=False)
            hackathon.organizer = request.user  # Set the current user as the organizer
            hackathon.save()
            return redirect('home')  # Redirect to the list of hackathons
    else:
        form = HackathonForm()
    return render(request, 'accounts/create_hackaton.html', {'form': form})


@staff_member_required  # Restrict access to staff members (admins)
def manage_organizer_requests(request):
    pending_requests = RequestToBeOrganizer.objects.filter(is_approved=False)
    return render(request, 'admin/manage_requests.html', {'pending_requests': pending_requests})

@staff_member_required
def approve_organizer_request(request, request_id):
    organizer_request = get_object_or_404(RequestToBeOrganizer, id=request_id)
    organizer_request.is_approved = True
    organizer_request.save()
    
    """ send_mail(
        'Your Organizer Request Has Been Approved',
        'Congratulations! You are now an approved organizer.',
        'admin@example.com',
        [organizer_request.user.email],
        fail_silently=False,
    ) """
     
    return redirect('manage_organizer_requests')


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
                login(request, user)
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

def welcome(request):
    return render(request, 'accounts/welcome.html')

def logout_view(request):
    logout(request)
    return render(request, 'accounts/welcome.html')

@login_required
def home(request):
    # Get all hackathons available for participants
    hackathons = Hackathon.objects.all()

    # Check if the user is an organizer (optional: based on the organizer request approval)
    try:
        organizer_request = RequestToBeOrganizer.objects.get(user=request.user)
        if organizer_request.is_approved:
            user_role = 'organizer'
        else:
            user_role = 'participant'
    except RequestToBeOrganizer.DoesNotExist:
        user_role = 'participant'
    
    return render(request, 'accounts/home.html', {'hackathons': hackathons, 'user_role': user_role})


def profile(request):
    return render(request, 'accounts/profile.html')

def settings(request):
    return render(request, 'accounts/settings.html')

@login_required
def hackathon_details(request, hackathon_id):
    # Get the details of a specific hackathon
    hackathon = get_object_or_404(Hackathon, id=hackathon_id)
    
    # Check if the user has already registered
    is_registered = Registration.objects.filter(user=request.user, hackathon=hackathon).exists()

    return render(request, 'accounts/hackathon_details.html', {
        'hackathon': hackathon,
        'is_registered': is_registered
    })
    
@login_required
def register_for_hackathon(request, hackathon_id):
    hackathon = get_object_or_404(Hackathon, id=hackathon_id)

    if hackathon.participants.filter(id=request.user.id).exists():
        return HttpResponseForbidden("You are already registered for this hackathon.")

    if request.method == 'POST':
        form = RegistrationForm(request.POST, hackathon=hackathon)
        if form.is_valid():
        # Pass the user and hackathon explicitly
          registration = form.save(commit=False, user=request.user, hackathon=hackathon)
          registration.save()  # Save the instance
          return redirect('home')
    else:
        form = RegistrationForm(hackathon=hackathon)
    return render(request, 'accounts/register_for_hackathon.html', {'form': form, 'hackathon': hackathon})