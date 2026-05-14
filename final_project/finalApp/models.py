from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	bio = models.TextField(blank= True)
	student_id = models.IntegerField(blank = True, null=True)
	major = models.CharField(max_length=100, blank=True, default="")
	interests = models.CharField(max_length=255, blank=True, default="")
	enrolled = models.BooleanField(default='True')

	def __str__(self):
		return self.user.username
	
class Club(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(max_length=120, blank=True, default="")
	image = models.ImageField(upload_to="club_images/", blank=True, null=True)
	desc = models.TextField()
	meetTimes = models.CharField(max_length=100)
	category = models.CharField(max_length=100, default="General")
	emailContact = models.EmailField(blank=True, default="")
	tag1 = models.CharField(max_length= 100, default="")
	tag2 = models.CharField(max_length= 100, blank=True, default="")

	def save(self, *args, **kwargs):
		if not self.slug:
			base_slug = slugify(self.name) or "club"
			slug = base_slug
			counter = 2

			while Club.objects.filter(slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1

			self.slug = slug
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name

	@property
	def initials(self):
		words = [word for word in self.name.split() if word]
		if len(words) >= 2:
			return f"{words[0][0]}{words[1][0]}".upper()
		return self.name[:2].upper() or "CL"

	@property
	def channel(self):
		return self.slug or slugify(self.name)

	@property
	def summary(self):
		return self.desc

	@property
	def meeting(self):
		return self.meetTimes

	@property
	def member_count_label(self):
		count = self.memberships.count()
		if count == 1:
			return "1 member"
		return f"{count} members"

	@property
	def tag_list(self):
		return [tag for tag in [self.category, self.tag1, self.tag2] if tag]

	@property
	def dot_class(self):
		label = f"{self.name} {self.category} {self.tag1} {self.tag2}".lower()
		if "sport" in label or "climb" in label:
			return "dot-orange"
		if "dev" in label or "software" in label or "coding" in label:
			return "dot-green"
		return "dot-teal"


class ClubMembership(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="memberships")
	# Club admins are allowed to create events from their club hub.
	is_admin = models.BooleanField(default=False)
	joined_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("user", "club")

	def __str__(self):
		return f"{self.user.username} in {self.club.name}"
  
class Event(models.Model):
	"""Scheduled club activity shown on the club Events tab."""

	# The FK keeps events scoped to one club space
	club = models.ForeignKey(
		Club,
		on_delete=models.CASCADE,
		related_name="events",
		null=True,
		blank=True,
	)
	title = models.CharField(max_length=120, default="")
	description = models.TextField(blank=True, default="")
	start_time = models.DateTimeField(default=timezone.now)
	end_time = models.DateTimeField(null=True, blank=True)
	location = models.CharField(max_length=120, blank=True, default="")
	requirements = models.CharField(max_length=255, blank=True, default="")
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		related_name="created_events",
		null=True,
		blank=True,
	)
	created_at = models.DateTimeField(default=timezone.now, editable=False)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ("start_time",)

	def clean(self):
		# Only validate the range when the optional end time is present.
		if self.end_time and self.end_time <= self.start_time:
			raise ValidationError("Event end time must be after the start time.")

	def __str__(self):
		if self.club:
			return f"{self.title} - {self.club.name}"
		return self.title
	
class ChatMessage(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


@receiver(post_save,sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.get_or_create(user=instance, defaults= {"student_id": 0})
