from django import forms
from .models import Hackathon, RequestToBeOrganizer, Registration , Team
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
        
class RequestToBeOrganizerForm(forms.ModelForm):
    class Meta:
        model = RequestToBeOrganizer
        fields = ['user','entity', 'topic']


class HackathonForm(forms.ModelForm):
    class Meta:
        model = Hackathon
        fields = ['title', 'description', 'start_date', 'end_date', 'location', 'rules_file', 'schedule', 'cover_photo']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'schedule': forms.Textarea(attrs={'rows': 2, 'cols': 30}),
        }

class RegistrationForm(forms.ModelForm):
    team_name = forms.CharField(max_length=100, required=False, label="Team Name")
    team = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Join a Team (Optional)"
    )

    # Adding three fields for additional members (team members)
    member_1 = forms.CharField(max_length=100, required=False, label="Team Member 1")
    member_2 = forms.CharField(max_length=100, required=False, label="Team Member 2")
    member_3 = forms.CharField(max_length=100, required=False, label="Team Member 3")

    class Meta:
        model = Registration
        fields = ['team', 'team_name', 'member_1', 'member_2', 'member_3']

    def __init__(self, *args, **kwargs):
        hackathon = kwargs.pop('hackathon', None)  # Pop the hackathon from kwargs
        super().__init__(*args, **kwargs)

        # Filter teams based on the provided hackathon
        if hackathon:
            self.fields['team'].queryset = hackathon.teams.all()

    def clean(self):
        cleaned_data = super().clean()
        team_name = cleaned_data.get('team_name')
        team = cleaned_data.get('team')

        if team_name and team:
            raise forms.ValidationError(
                "You cannot create a team and join an existing team at the same time."
            )

        if not team_name and not team:
            raise forms.ValidationError(
                "You must either create a team or join an existing team."
            )

        # Validate additional team members if creating a team
        if team_name:
            for field in ['member_1', 'member_2', 'member_3']:
                username = cleaned_data.get(field)
                if username:
                    if not User.objects.filter(username=username).exists():
                        self.add_error(field, f"User '{username}' does not exist.")

        return cleaned_data

    def save(self, commit=True, user=None, hackathon=None):  # Accept user and hackathon
        
        if not user or not hackathon:
            raise ValueError("Both 'user' and 'hackathon' must be provided to save the form.")


        instance = super().save(commit=False)
        instance.user = user  # Set the user
        instance.hackathon = hackathon  # Set the hackathon

        # Handle team creation
        if self.cleaned_data['team_name']:
            team = Team.objects.create(
                hackathon=hackathon,
                name=self.cleaned_data['team_name']
            )
            team.members.add(user)

            # Add additional team members
            for field in ['member_1', 'member_2', 'member_3']:
                username = self.cleaned_data.get(field)
                if username:
                    try:
                        member = User.objects.get(username=username)
                        team.members.add(member)
                    except User.DoesNotExist:
                        pass

            instance.team = team

        elif self.cleaned_data['team']:
            instance.team = self.cleaned_data['team']

        if commit:
            instance.save()

        return instance
