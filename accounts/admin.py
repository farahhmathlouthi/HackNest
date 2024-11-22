from django.contrib import admin
from .models import RequestToBeOrganizer, Hackathon, Team

admin.site.register(RequestToBeOrganizer)
admin.site.register(Hackathon)
admin.site.register(Team)
