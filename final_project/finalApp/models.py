from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Club class
# Clubs should have name, major most aligned with, relevant tags associated with club

class Tag(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    

class Club(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    #Club can have multiple tags
    tags = models.ManyToManyField(Tag)
    requirements = models.TextField()
    amenities = models.TextField()
    member_count = models.IntegerField(default=0)
    cover_image = models.ImageField(upload_to='club_covers/', blank=True)
    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag)          # for matching with clubs
    liked_clubs = models.ManyToManyField(Club, related_name='liked_by', blank=True)
    passed_clubs = models.ManyToManyField(Club, related_name='passed_by', blank=True)

    def __str__(self):
        return self.user.username
    

