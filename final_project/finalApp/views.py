from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Club, Profile


def app_context(request, **extra):
    if request.user.is_authenticated:
        club_spaces = Club.objects.filter(memberships__user=request.user).order_by("name")
    else:
        club_spaces = Club.objects.none()

    context = {"club_spaces": club_spaces}
    context.update(extra)
    return context


def build_register_form(data=None):
    form = UserCreationForm(data)
    form.fields["username"].help_text = "Use letters, numbers, and @ . + - _ only."
    form.fields["password1"].help_text = "Use 8+ characters and avoid something too common."
    form.fields["password2"].help_text = "Enter the same password again."
    return form


@login_required
def home(request):
    return render(request, 'home.html', app_context(request))

@login_required
def club_match(request):
    club = Club.objects.first()
    return render(request, 'club_match.html', app_context(request, club=club))


@login_required
def club_hub(request, club_slug):
    active_club = get_object_or_404(
        Club.objects.filter(memberships__user=request.user),
        slug=club_slug,
    )

    return render(
        request,
        "club_hub.html",
        app_context(request, active_club=active_club),
    )


def register(request):
    if request.method == "POST":
        form = build_register_form(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully")
            return redirect("login")
    else:
        form = build_register_form()

    return render(request, "register.html", {"form": form})


@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"student_id": 0},
    )
    return render(request, "profile.html", app_context(request, profile=profile))
