from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Profile

@login_required
def home(request):
    return render(request, 'home.html', {})

def club_match(request):
    return render(request, 'club_match.html')


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully")
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "profile.html", {"profile": profile})
