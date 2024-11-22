from django.db import models
from django.contrib.auth.models import User


class RequestToBeOrganizer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    entity = models.TextField()  
    topic = models.TextField()   
    is_approved = models.BooleanField(default=False)
    date_requested = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request from {self.user.username} - {'Approved' if self.is_approved else 'Pending'}"



class Hackathon(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200) 
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    rules_file = models.FileField(upload_to='hackathon_rules/', null=True, blank=True)  # File for rules
    schedule = models.TextField(null=True, blank=True)  # Text area for planning/schedule
    
    cover_photo = models.ImageField(upload_to='hackathon_covers/', null=True, blank=True)
     
    participants = models.ManyToManyField(User, related_name='registered_hackathons', blank=True)  # Added participants

    def __str__(self):
        return self.title
    
    

class Team(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='teams')

    def __str__(self):
        return f'{self.name} ({self.hackathon})'

class Registration(models.Model):
    team_name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.user.username} registered for {self.hackathon.name}'
