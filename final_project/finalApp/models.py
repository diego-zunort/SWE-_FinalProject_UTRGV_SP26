from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	bio = models.TextField(blank= True)
	student_id = models.IntegerField(blank = True, null=True)
	major = models.CharField(max_length=100, blank=True, default="")
	interests = models.CharField(max_length=255, blank=True, default="")

	def __str__(self):
		return self.user.username
	
class Club(models.Model):
	name = models.CharField(max_length=100)
	desc = models.TextField()
	meetTimes = models.CharField(max_length=100)
	category = models.CharField(max_length=100, default="General")
	emailContact = models.EmailField(blank=True, default="")
	tag1 = models.CharField(max_length= 100, default="")
	tag2 = models.CharField(max_length= 100, blank=True, default="")

	def __str__(self):
		return self.name
