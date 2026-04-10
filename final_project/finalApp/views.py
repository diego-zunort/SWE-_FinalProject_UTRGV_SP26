from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html', {})
def club_match(request):
    return render(request, 'club_match.html')