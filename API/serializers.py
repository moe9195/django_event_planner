from rest_framework import serializers
from django.contrib.auth.models import User
from events.models import Event, Booking, Profile

class FollowingSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    date_followed = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ['username', 'date_followed']

    def get_username(self, obj):
        return obj.user.username
    def get_date_followed(self, obj):
        return obj.user.date_joined

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class EventsSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    seats_left = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['owner', 'title', 'description', 'location', 'date', 'time', 'price', 'totalseats', 'seats_left']

    def get_seats_left(self, obj):
        return obj.seats_left()

class UserEventsSerializer(serializers.ModelSerializer):
    seats_left = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['owner', 'title', 'description', 'location', 'date', 'time', 'price', 'totalseats', 'seats_left']

    def get_seats_left(self, obj):
        return obj.seats_left()

class BookSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    event = EventsSerializer()
    class Meta:
        model = Booking
        fields = ['user', 'event', 'ticketnums', 'booking_date', 'booking_time']

class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'date', 'time', 'price', 'totalseats']

class BookedUsersSerializer(serializers.ModelSerializer):
    booked_by = serializers.SerializerMethodField()
    tickets_sold = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['id', 'title', 'tickets_sold', 'booked_by']

    def get_tickets_sold(self, obj):
        return obj.seats_booked()

    def get_booked_by(self, obj):
        booked_by = obj.bookings.all()
        booked_by_users = []
        for user in booked_by:
            booked_by_users.append(user.user)
        serializer = UserSerializer(booked_by_users, many=True)
        return serializer.data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        email = validated_data['email']
        new_user = User(username=username, first_name=first_name, last_name=last_name, email=email)
        new_user.set_password(password)
        new_user.save()
        return validated_data
