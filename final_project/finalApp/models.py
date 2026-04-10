from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	bio = models.TextField(blank= True)
	student_id = models.IntegerField(blank = True)
	enrolled = models.BooleanField(default=True)


	def __str__(self):
		return self.user.username