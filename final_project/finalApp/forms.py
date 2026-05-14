from django import forms
from django.contrib.auth.models import User
from .models import Profile, Club, Event

# Shared class applied to event widgets so the modal can style them consistently.
EVENT_INPUT_CLASS = "event-input"

class ProfileForm(forms.ModelForm):
    Major_Choices = [
        ('','Select your major'),
        ('Computer Science', 'Computer Science'),
        ('Engineering','Engineering'),
        ('Business','Business'),
        ('Biology','Biology'),
        ('Art','Art'),
        ('Education','Education'),
        ('Nursing','Nursing'),
        ('Political Science','Political Science')
    ]
    Interest_Choices = [
        ('Technology','Technology'),
        ('Engineering','Engineering'),
        ('Health','Health'),
        ('Sports','Sports'),
        ('Gaming','Gaming'),
        ('Music','Music'),
        ('Media','Media'),
        ('Art','Art'),
        ('Books','Books'),
        ('Anime','Anime'),
        ('Social','Social'),
        ('Astronomy','Astronomy'),
        ('Intramural','Intramural'),
        ('Environment','Environment'),
        ('Science','Science')
    ]
    major = forms.ChoiceField(choices=Major_Choices)
    interests = forms.MultipleChoiceField(choices=Interest_Choices,
                                          widget=forms.CheckboxSelectMultiple)
    
    #caps users at 2
    def clean_interests(self):
        interests = self.cleaned_data.get('interests')
        if len(interests) > 2:
            raise forms.ValidationError('Please select a maximum of 2 interests.')
        return interests

    class Meta:
        model = Profile
        fields = ['bio','major','interests','student_id']

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name','desc','meetTimes','category','emailContact','tag1','tag2']

class EventForm(forms.ModelForm):
    """Form club admins use to create events from the club hub dialog."""

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "start_time",
            "end_time",
            "location",
            "requirements",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": EVENT_INPUT_CLASS, "placeholder": "Event title"}),
            "description": forms.Textarea(attrs={"class": EVENT_INPUT_CLASS, "rows": 4, "placeholder": "What should members know?"}),
            "start_time": forms.DateTimeInput(attrs={"class": EVENT_INPUT_CLASS, "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "end_time": forms.DateTimeInput(attrs={"class": EVENT_INPUT_CLASS, "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "location": forms.TextInput(attrs={"class": EVENT_INPUT_CLASS, "placeholder": "Location"}),
            "requirements": forms.TextInput(attrs={"class": EVENT_INPUT_CLASS, "placeholder": "Optional requirements"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Browser datetime-local inputs post values in this exact format.
        self.fields["start_time"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_time"].input_formats = ["%Y-%m-%dT%H:%M"]
        # These fields can be filled in later, so admins can create a simple event quickly.
        self.fields["end_time"].required = False
        self.fields["description"].required = False
        self.fields["location"].required = False
        self.fields["requirements"].required = False
