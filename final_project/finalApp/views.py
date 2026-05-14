from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from datetime import timedelta
from django.urls import reverse

from .models import Club, Profile, ClubMembership, ChatMessage, Event
from .forms import EventForm, ProfileForm

def app_context(request, **extra):
    if request.user.is_authenticated:
        club_spaces = Club.objects.filter(memberships__user=request.user).order_by("name")
        upcoming_events = (
            Event.objects.filter(club__memberships__user=request.user, start_time__gte=timezone.now())
            .select_related("club")
            .order_by("start_time")
        )[:5]

        today = timezone.localdate()
        week_start = today - timedelta(days=(today.weekday() + 1) % 7)
        mini_calendar_days = [week_start + timedelta(days=offset) for offset in range(7)]
    else:
        club_spaces = Club.objects.none()
        upcoming_events = Event.objects.none()
        mini_calendar_days = []
        today = timezone.localdate()

    context = {
        "club_spaces": club_spaces,
        "upcoming_events": upcoming_events,
        "mini_calendar_days": mini_calendar_days,
        "mini_calendar_today": today,
        "mini_calendar_month_label": today.strftime("%B"),
    }
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
def calendar(request):
    return render(request, "calendar.html", app_context(request))


@login_required
def calendar_redirect(request):
    return redirect("calendar")


@login_required
def my_events_feed(request):
    start = parse_datetime(request.GET.get("start") or "")
    end = parse_datetime(request.GET.get("end") or "")
    if not start or not end:
        return JsonResponse({"detail": "Missing start/end query params."}, status=400)

    if timezone.is_naive(start):
        start = timezone.make_aware(start, timezone.get_current_timezone())
    if timezone.is_naive(end):
        end = timezone.make_aware(end, timezone.get_current_timezone())

    events = (
        Event.objects.filter(
            club__memberships__user=request.user,
        )
        .filter(
            Q(end_time__isnull=True, start_time__gte=start, start_time__lt=end)
            | Q(end_time__gt=start, start_time__lt=end)
        )
        .select_related("club")
        .order_by("start_time")
    )

    payload = []
    for event in events:
        if not event.club:
            continue
        payload.append(
            {
                "id": event.pk,
                "title": event.title,
                "start": event.start_time.isoformat(),
                "end": event.end_time.isoformat() if event.end_time else None,
                "url": f"{reverse('club_hub', kwargs={'club_slug': event.club.slug})}?tab=events",
                "extendedProps": {
                    "club": event.club.name if event.club else "",
                    "location": event.location,
                    "requirements": event.requirements,
                },
            }
        )

    return JsonResponse(payload, safe=False)

@login_required
def club_match(request):
    club = Club.objects.order_by('?').first()
    return render(request, 'club_match.html', app_context(request, club=club))


@login_required
def club_hub(request, club_slug):
    # Users can only open hub pages for clubs they have joined.
    active_club = get_object_or_404(
        Club.objects.filter(memberships__user=request.user),
        slug=club_slug,
    )
    # The membership record also tells us whether this user can manage events.
    membership = get_object_or_404(
        ClubMembership,
        user=request.user,
        club=active_club,
    )
    # One hub view powers both Slack-style tabs: messages and events.
    active_tab = request.GET.get("tab", "messages")
    if active_tab not in {"messages", "events"}:
        active_tab = "messages"

    club_messages = active_club.messages.select_related("author").order_by("timestamp")
    club_events = active_club.events.select_related("created_by").order_by("start_time")
    event_form = EventForm()

    if request.method == "POST" and request.POST.get("action") == "create_event":
        # Never trust the hidden form action alone; verify admin status server-side.
        if not membership.is_admin:
            raise PermissionDenied("Only club admins can create events.")

        event_form = EventForm(request.POST)
        active_tab = "events"
        if event_form.is_valid():
            event = event_form.save(commit=False)
            # Scope the new event to the active club instead of trusting posted data.
            event.club = active_club
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created.")
            return redirect(f"{request.path}?tab=events")

    return render(
        request,
        "club_hub.html",
        app_context(
            request,
            active_club=active_club,
            active_tab=active_tab,
            club_messages=club_messages,
            club_events=club_events,
            event_form=event_form,
            is_club_admin=membership.is_admin,
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
    
