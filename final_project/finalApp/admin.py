from django.contrib import admin

# Register your models here.
from .models import Club, Tag, Student

admin.site.register(Student)
admin.site.register(Club)
