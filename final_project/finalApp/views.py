from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Club, Profile, ClubMembership, ChatMessage
from .forms import ProfileForm

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

#matching algorithm
def get_next_match(user):
    profile, _ = Profile.objects.get_or_create(user=user , defaults= {"student_id":0}) #gets current logged in user
    user_interests = profile.interests.split(', ') if profile.interests else []
    user_major = profile.major if profile.major else ''
    #get user interests + major

    #gets all clubs already joined for user
    #returns them by id
    joined_clubs = ClubMembership.objects.filter(user=user).values_list('club_id',flat = True)
    #excludes clubs already joined from search by checkking list
    #__in djangos way to lookup by types
    available_clubs = Club.objects.exclude(id__in = joined_clubs)
    matched_club = None
    for club in available_clubs:
        if (user_major in [club.category, club.tag1, club.tag2] or any(interest in [club.category,club.tag1,club.tag2] for interest in user_interests)):
            matched_club = club
            break
    #if no matches in db then display random club
    if not matched_club:
        matched_club = available_clubs.order_by('?').first()
    return matched_club


@login_required
def home(request):
    next_match = get_next_match(request.user)
    latest_membership = ClubMembership.objects.filter(user = request.user).order_by('-id').first()
    recent_club = latest_membership.club if latest_membership else None
    general_messages = ChatMessage.objects.filter(
        club = None
    ).order_by('timestamp')
    return render(request, 'home.html', app_context(request, next_match=next_match, recent_club = recent_club,general_messages=general_messages))

@login_required
def club_match(request):
    club = Club.objects.order_by('?').first()
    return render(request, 'club_match.html', app_context(request, club=club))


@login_required
def club_hub(request, club_slug):
    active_club = get_object_or_404(
        Club.objects.filter(memberships__user=request.user),
        slug=club_slug,
    )

    club_messages = active_club.messages.select_related("author").order_by("timestamp")

    return render(
        request,
        "club_hub.html",
        app_context(
            request,
            active_club=active_club,
            club_messages=club_messages,
        ),
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
            interests_list = form.cleaned_data.get('interests', [])
            profile_instance.interests = ', '.join(interests_list)
            profile_instance.enrolled = form.cleaned_data['enrolled'] == 'True'
            student_id = form.cleaned_data.get('student_id')
            profile_instance.student_id = student_id if student_id else None
            profile_instance.save()
            return redirect('home')
        else:
            print(form.errors)
    else:
        saved_interests = profile.interests.split(', ') if profile.interests else []
        form =  ProfileForm(instance=profile, initial={'interests': saved_interests})
    
    return render(request, "profile.html", app_context(request, profile=profile, form=form))

@login_required
def join_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    ClubMembership.objects.get_or_create(user=request.user, club=club)
    return redirect('club_hub',club_slug = club.slug)

@login_required
def leave_club(request, club_id):
    club = get_object_or_404(Club, id = club_id)
    ClubMembership.objects.filter(user=request.user, club=club).delete()
    return redirect('home')

@login_required
def skip_club(request,club_id):
    joined_clubs = ClubMembership.objects.filter(user=request.user).values_list('club_id',flat = True)
    club = Club.objects.exclude(id=club_id).exclude(id__in = joined_clubs).order_by('?').first()
    return render(request, 'club_match.html', app_context(request, club=club))

@login_required
def club_match(request):
    club = get_next_match(request.user)
    return render(request, 'club_match.html',app_context(request,club=club))
    

