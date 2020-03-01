from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from events.models import Event, Booking
from django.http import JsonResponse
from .permissions import IsOwner
from datetime import datetime
from .serializers import (
        EventsSerializer,
        #UserEventsSerializer,
        RegisterSerializer,
        BookSerializer,
        CreateEventSerializer,
        BookedUsersSerializer,
        )


class UpcomingEventsList(ListAPIView):
    serializer_class = EventsSerializer

    def get_queryset(self):
        return Event.objects.filter(date__gte=datetime.today()).order_by("date")

# class UserEventsList(ListAPIView):
#     serializer_class = UserEventsSerializer
#     permission_classes = [AllowAny]
#
#     def get_queryset(self):
#         return Event.objects.filter(owner=self.owner)

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
