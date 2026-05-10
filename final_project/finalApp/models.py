from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	bio = models.TextField(blank= True)
	student_id = models.IntegerField(blank = True)
	enrolled = models.BooleanField(default=True)


	def __str__(self):
		return self.user.username
	
class Club(models.Model) :
	name = models.CharField(max_length=100)
	desc = models.TextField()
	meetTimes = models.CharField(max_length=100)
	
	def __str__(self):
		return self.name

class Event(models.Model):

	eventName = models.CharField(max_length=100)
	desc = models.TextField()
	time = models.CharField(max_length=100)
	location = models.CharField(max_length=100)
	hostClub = models.CharField(max_length=100)
	requirements = models.CharField(max_length=100)

	def __str__(self):
		return self.name
	
class ChatMessage(models.Model):

	club = models.CharField(max_length=100)
	author = models.CharField(max_length=100)
	message = models.TextField()
	timestamp = models.CharField(max_length=100)

	def __str__(self):
		return self.name