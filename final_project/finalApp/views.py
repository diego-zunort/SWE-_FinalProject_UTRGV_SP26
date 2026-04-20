from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html', {})

def clubs(request):
    return render(request, 'clubs.html')

def club_match(request):
    return render(request, 'club_match.html')

def create_a_club(request):
    return render(request, 'create_a_club.html')