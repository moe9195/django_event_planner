"""event_planner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import API.views as apiviews
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),

    path('api/login/', TokenObtainPairView.as_view(), name="api-login"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name="token-refresh"),
    path('api/register/', apiviews.Register.as_view(), name="api-register"),

    # list of all upcoming events
    path('api/eventlist/', apiviews.UpcomingEventsList.as_view(), name='api-list'),

    # list of all events booked by the user
    path('api/eventlist/booked/', apiviews.BookedEventsList.as_view(), name='api-booked-list'),

    # api for creating a new event
    path('api/create/', apiviews.CreateEvent.as_view(), name='api-create'),

    # api for updating an existing event
    path('api/update/<int:event_id>/', apiviews.UpdateEvent.as_view(), name='api-update'),

    # lists to the owner the users who booked a specific event
    path('api/bookedby/<int:event_id>/', apiviews.EventBookedBy.as_view(), name='api-bookedby'),

    # lists to the owner the users who booked a specific event
    path('api/book/<int:event_id>/', apiviews.BookEvent.as_view(), name='api-book'),

    # list of all user events
    path('api/eventlist/<str:username>/', apiviews.UserEventsList.as_view(), name='api-user-events'),

    # List of all users that the logged in user is following
    path('api/following/', apiviews.FollowingList.as_view(), name='user-follows'),

    # api to follow/unfollow a specific organizer
    path('api/follow/', apiviews.FollowOrganizer.as_view(), name='follow-user'),


]


if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
