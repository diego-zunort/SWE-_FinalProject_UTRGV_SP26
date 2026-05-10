from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from .models import Club, Profile
from .forms import ProfileForm

CLUB_SPACES = [
    {
        "slug": "robotics-lab",
        "name": "Robotics Lab",
        "initials": "RL",
        "channel": "robotics-lab",
        "dot_class": "dot-teal",
        "summary": "Build nights, hardware projects, competition planning, and student maker support.",
        "meeting": "Wednesdays at 5:30 PM",
        "members": "42 members",
        "next_event": "Line-following robot demo",
        "tags": ["Robotics", "Engineering", "Beginner friendly"],
        "channels": ["announcements", "build-help", "competition-team"],
        "messages": [
            {
                "author": "Venture Bot",
                "time": "9:00 AM",
                "avatar": "V",
                "body": "Welcome to Robotics Lab. This space is for build updates, meeting notes, and project help.",
            },
            {
                "author": "John Testerson",
                "time": "10:12 AM",
                "avatar": "JT",
                "body": "Bring laptops and any Arduino kits you have. We are pairing new members with returning teams tonight.",
            },
        ],
    },
    {
        "slug": "utrgv-club-sports-climbing",
        "name": "UTRGV Club Sports Climbing",
        "initials": "CC",
        "channel": "club-sports-climbing",
        "dot_class": "dot-orange",
        "summary": "Training sessions, climbing trips, safety check-ins, and outdoor recreation planning.",
        "meeting": "Mondays and Thursdays at 6:00 PM",
        "members": "28 members",
        "next_event": "Intro belay clinic",
        "tags": ["Sports", "Outdoors", "Training"],
        "channels": ["announcements", "routes", "trip-planning"],
        "messages": [
            {
                "author": "Venture Bot",
                "time": "9:05 AM",
                "avatar": "V",
                "body": "Welcome to Club Sports Climbing. Check announcements for practice times and trip signups.",
            },
            {
                "author": "Michaela Testa",
                "time": "11:20 AM",
                "avatar": "MT",
                "body": "New climbers are welcome at the intro clinic. No gear required for the first session.",
            },
        ],
    },
    {
        "slug": "frontera-devs",
        "name": "Frontera Devs",
        "initials": "FD",
        "channel": "frontera-devs",
        "dot_class": "dot-green",
        "summary": "Software projects, hack nights, portfolio feedback, and peer coding help.",
        "meeting": "Fridays at 4:00 PM",
        "members": "36 members",
        "next_event": "Portfolio review night",
        "tags": ["Software", "Hackathons", "Career prep"],
        "channels": ["announcements", "project-ideas", "code-help"],
        "messages": [
            {
                "author": "Venture Bot",
                "time": "9:10 AM",
                "avatar": "V",
                "body": "Welcome to Frontera Devs. Share project ideas, ask for code help, and find teammates here.",
            },
            {
                "author": "Testy McTestface",
                "time": "1:04 PM",
                "avatar": "TM",
                "body": "I opened a thread for resume site feedback. Drop your GitHub link when you are ready.",
            },
        ],
    },
]


def app_context(**extra):
    context = {"club_spaces": CLUB_SPACES}
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
    return render(request, 'home.html', app_context())

@login_required
def club_match(request):
    club = Club.objects.first()
    return render(request, 'club_match.html', app_context(club=club))


@login_required
def club_hub(request, club_slug):
    active_club = next(
        (club_space for club_space in CLUB_SPACES if club_space["slug"] == club_slug),
        None,
    )

    if active_club is None:
        raise Http404("Club space not found")

    return render(
        request,
        "club_hub.html",
        app_context(active_club=active_club),
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
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile_instance = form.save(commit=False)
            interests_list = form.cleaned_data['interests']
            profile_instance.interests = ', '.join(interests_list)
            profile_instance.save()
            return redirect('home')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, "profile.html", {'form':form, 'profile': profile})
