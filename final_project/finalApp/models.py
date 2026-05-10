from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	bio = models.TextField(blank= True)
	student_id = models.IntegerField(blank = True)
	enrolled = models.BooleanField(default=True)


	def __str__(self):
		return self.user.username
	
class Club(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(max_length=120, blank=True, default="")
	desc = models.TextField()
	meetTimes = models.CharField(max_length=100)
	category = models.CharField(max_length=100, default="General")
	emailContact = models.EmailField(blank=True, default="")
	insta = models.URLField(blank=True, default="")
	vLink = models.URLField(blank=True, default="")
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
	joined_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("user", "club")

	def __str__(self):
		return f"{self.user.username} in {self.club.name}"
