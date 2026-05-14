from django import forms
from django.contrib.auth.models import User
from .models import Profile, Club

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

    Enrolled_Choices =[(True,'Enrolled'),(False,'Not Enrolled')]
    enrolled = forms.ChoiceField(choices=Enrolled_Choices)
    major = forms.ChoiceField(choices=Major_Choices)
    interests = forms.MultipleChoiceField(choices=Interest_Choices,
                                          widget=forms.CheckboxSelectMultiple)
    
    def clean_interests(self):
        interests = self.cleaned_data.get('interests')
        return interests

    class Meta:
        model = Profile
        fields = ['bio','major','interests','student_id','enrolled']

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name','desc','meetTimes','category','emailContact','tag1','tag2']
