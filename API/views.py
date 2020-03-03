from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from events.models import Event, Booking, Profile
from django.contrib.auth.models import User
from django.http import JsonResponse
from .permissions import IsOwner
from datetime import datetime
from django.db.models import Q
from .serializers import (
        EventsSerializer,
        UserEventsSerializer,
        RegisterSerializer,
        BookSerializer,
        CreateEventSerializer,
        BookedUsersSerializer,
        FollowingSerializer,
        )

class FollowOrganizer(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        username = request.data.get('username')
        if username == request.user:
            return JsonResponse({"error": "You cannot follow yourself!"})
        obj_user = User.objects.get(username=username)
        user = User.objects.get(id=obj_user.id)
        profile = Profile.objects.get(user=user)
        if profile.follows.filter(user=request.user):
            profile.follows.remove(request.user.profile)
            profile.save()
            return JsonResponse({"success": "User unfollowed successfully."})
        else:
            profile.follows.add(request.user.profile)
            profile.save()
            return JsonResponse({"success": "User followed successfully."})


class FollowingList(ListAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        profile = Profile.objects.get(user=user)
        follows = user.profile.followed_by.filter(~Q(user=self.request.user))
        follows = [f for f in follows]
        return follows

class UpcomingEventsList(ListAPIView):
    serializer_class = EventsSerializer

    def get_queryset(self):
        return Event.objects.filter(date__gte=datetime.today()).order_by("date")

class UserEventsList(ListAPIView):
    serializer_class = UserEventsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs['username']
        return Event.objects.filter(owner__username=username)

class BookedEventsList(ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class CreateEvent(CreateAPIView):
    serializer_class = CreateEventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UpdateEvent(RetrieveUpdateAPIView):
    queryset = Event.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'event_id'
    serializer_class = CreateEventSerializer(many=True)
    permission_classes = [IsAuthenticated, IsOwner]

class EventBookedBy(RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = BookedUsersSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'event_id'
    permission_classes = [IsAuthenticated, IsOwner]

class BookEvent(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, event_id):
        tickets = request.data.get('tickets')
        if tickets.isdigit():
            tickets = int(tickets)
        else:
            return JsonResponse({"error": tickets+" is not a valid number. Please enter a valid number"})
        event = Event.objects.get(id=event_id)
        if tickets < event.seats_left():
            Booking.objects.create(user=request.user, event=event, ticketnums=tickets)
            return JsonResponse({"success": "Booking created successfully."})
        else:
            return JsonResponse({"error": "Not enough seats left, please buy less tickets ("+str(event.seats_left())+" seats left)."})


class Register(CreateAPIView):
    serializer_class = RegisterSerializer
