"""
URL configuration for final project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from finalApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True)),
    path('home/', views.home, name='home'),
    path('home/calendar', views.calendar_redirect),
    path('home/calendar/', views.calendar_redirect),
    path('calendar/', views.calendar, name='calendar'),
    path('api/events/', views.my_events_feed, name='my_events_feed'),
    path('club_match/', views.club_match, name='club_match'),
    path('clubs/<str:club_slug>/', views.club_hub, name='club_hub'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('join/<int:club_id>/', views.join_club, name='join_club'),
    path('skip/<int:club_id>/', views.skip_club,name='skip_club'),
    path('leave/<int:club_id>/', views.leave_club, name='leave_club')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
