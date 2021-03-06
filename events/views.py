from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import UserSignup, UserLogin, EventForm, BookForm, ProfileForm, UserForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Event, Booking, Profile
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings


def FollowView(request, user_id):
    if request.user.is_anonymous:
        return redirect('login')
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    if profile.follows.filter(user=request.user):
        profile.follows.remove(request.user.profile)
        profile.save()
        return redirect('user-profile', user_id)
    else:
        profile.follows.add(request.user.profile)
        profile.save()
    return redirect('user-profile', user_id)


def ProfileView(request, user_id):
    if request.user.is_anonymous:
        return redirect('login')
    user = User.objects.get(id=user_id)
    print(user.profile) # have to access child object for it to be created
    profile = Profile.objects.get(user=user)
    if profile.follows.filter(user=request.user):
        button = False
    else:
        button = True
    followers = user.profile.follows.all()
    following = user.profile.followed_by.all()
    # need to make these two more efficient using SQL queries
    followers = [f.user for f in followers]
    following = [f.user for f in following]

    events = Event.objects.filter(owner=user)
    context = {
        "profile":profile,
        "user": user,
        "following": following,
        "followers": followers,
        "events": events,
        "button": button
    }
    return render(request, 'profile.html', context)

def UserEventsView(request, user_id):
    if request.user.is_anonymous:
        return redirect('login')
    events = Event.objects.filter(owner=user_id)
    context = {
        "events": events,
    }
    return render(request, 'my_events.html', context)

def UserListView(request):
    users = User.objects.all()
    context = {
        "users":users
    }
    return render(request, 'users_list.html', context)

def EventBookView(request, event_id):
    if request.user.is_anonymous:
        return redirect('login')
    event = Event.objects.get(id=event_id)
    form = BookForm()
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.event = event
            book.user = request.user
            available_seats = event.seats_left()
            if book.ticketnums > available_seats: # move up
                messages.warning(request, "Number of tickets exceeds available seats!")
            else:
                book.save()
                # sends email to user when they book if they have a valid email
                if request.user.email:
                    subject = 'Itinerary for the Reservation ' + str(book.id)
                    message =   f"""
                                BOOKING REFERENCE: {book.id}
                                =-=-=--=-=--=-=-=-=-=-=-=-=
                                DATE OF ISSUE: {book.booking_date}
                                TIME OF ISSUE: {book.booking_time}
                                NUMBER OF TICKETS: {book.ticketnums}
                                TOTAL IN USD: {book.price_paid()} ({book.event.price} x {book.ticketnums})
                                THANK YOU FOR YOUR PURCHASE!!!



                                EVENT DETAILS:
                                =-=-=--=-=--=-=-=-=-=-=-=-=
                                EVENT NAME: {book.event.title}
                                EVENT DESCRIPTION: {book.event.description}
                                EVENT ORGANIZER: {book.event.owner}
                                EVENT DATE: {book.event.date}
                                EVENT TIME: {book.event.time}
                                EVENT LOCATION: {book.event.location}
                                """

                    email_from = settings.EMAIL_HOST_USER
                    recipient = [request.user.email]
                    send_mail(subject, message, email_from, recipient)
                return redirect('booked-events')
    context = {
        "form":form,
        "event":event,
    }
    return render(request, 'book_event.html', context)

def CancelBookingView(request, booking_id):
    if request.user.is_anonymous:
        return redirect('login')
    booking = Booking.objects.get(id=booking_id)
    if booking.can_cancel():
        booking.delete()
        messages.success(request, ("Booking cancelled successfully."))
    else:
        messages.success(request, ("You can only cancel an event 3 hours before."))
    return redirect('booked-events')


def BookedEventsView(request):
    if request.user.is_anonymous:
        return redirect('login')
    bookings = Booking.objects.filter(user=request.user)
    context = {
        "bookings":bookings
    }
    return render(request, 'booked_events.html', context)

def EventHistoryView(request):
    if request.user.is_anonymous:
        return redirect('login')
    bookings = Booking.objects.filter(user=request.user)
    # you can do it through filter
    past_bookings = [booking for booking in bookings if (datetime.combine(booking.event.date, booking.event.time) <= datetime.now())]

    context = {
        "past_bookings":past_bookings
    }
    return render(request, 'event_history.html', context)

def AllEventsView(request):
    if request.user.is_anonymous:
        return redirect('login')
    today = datetime.today()
    events = Event.objects.filter(date__gte=today).exclude(owner=request.user).order_by("date")
    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(title__icontains=query)|
            Q(description__icontains=query)|
            Q(owner__username__icontains=query)
            ).distinct()
    context = {
        "events": events,
    }
    return render(request, 'all_events.html', context)

def DashboardView(request):
    if request.user.is_anonymous:
        return redirect('login')
    events = Event.objects.filter(owner=request.user)
    context = {
        "events": events
    }
    return render(request, 'dashboard.html', context)

def MyEventsView(request):
    if request.user.is_anonymous:
        return redirect('login')
    events = Event.objects.filter(owner=request.user)
    context = {
        "events": events
    }
    return render(request, 'my_events.html', context)

def UserEventsView(request, user_id):
    if request.user.is_anonymous:
        return redirect('login')
    user = User.objects.get(id=user_id)
    events = Event.objects.filter(owner=user)
    context = {
        "events": events,
        "user": user,
    }
    return render(request, 'user_events.html', context)

def EventDetailView(request, event_id):
    if request.user.is_anonymous:
        return redirect('login')
    event = Event.objects.get(id=event_id)
    bookings = Booking.objects.filter(event=event)
    context = {
        "event": event,
        "bookings":bookings,
    }
    return render(request, 'detail.html', context)

def EventCreateView(request):
    if request.user.is_anonymous:
        return redirect('login')
    form = EventForm(request.POST)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES or None)
        if form.is_valid():
            event = form.save(commit=False)
            event.owner = request.user
            event.save()
            messages.success(request, "Event created successfully.")
            return redirect('my-events')
    context = {
        "form":form,
    }
    return render(request, 'create_event.html', context)

def PasswordUpdateView(request, user_id):
    if request.user.is_anonymous:
        return redirect('login')
    user = User.objects.get(id=user_id)
    if request.user != user:
        messages.success(request, ('Only the owner can edit their profile.'))
        return redirect('user-profile', user_id)
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form)
            messages.success(request,"Profile updated successfully.")
            return redirect('user-profile', user_id)
        else:
            messages.success(request, ('Please correct the errors below.'))
    else:
        password_form = PasswordChangeForm(user)
    return render(request, 'edit_password.html', {
        'password_form': password_form,
    })

def ProfileUpdateView(request, user_id):
    if request.user.is_anonymous:
        return redirect('login')
    user = User.objects.get(id=user_id)
    if request.user != user:
        messages.success(request, ('Only the owner can edit their profile.'))
        return redirect('user-profile', user_id)
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"Profile updated successfully.")
            return redirect('user-profile', user_id)
        else:
            messages.success(request, ('Please correct the errors below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


def EventUpdateView(request, event_id):
    if request.user.is_anonymous:
        return redirect('login')
    event = Event.objects.get(id=event_id)
    if request.user != event.owner:
        return redirect('event-detail', event_id)
    form = EventForm(instance=event)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            event.owner = request.user      # no need because updating not creating
            event.save()
            messages.success(request, "Event updated successfully.")
            return redirect('event-detail', event_id)
    context = {
        "event": event,
        "form": form,
    }
    return render(request, 'edit_event.html', context)

# check if the person who is trying to delete is the owner
def EventDeleteView(request, event_id):
    if request.user.is_anonymous:
        return redirect('login')
    Event.objects.get(id=event_id).delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('my-events')

def home(request):
    return render(request, 'home.html')

def timer(request):
    return render(request, 'timer.html')

class Signup(View):
    form_class = UserSignup
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            messages.success(request, "You have successfully signed up.")
            login(request, user)
            return redirect("home")
        messages.warning(request, form.errors)
        return redirect("signup")


class Login(View):
    form_class = UserLogin
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                messages.success(request, "Welcome Back!")
                return redirect('dashboard')
            messages.warning(request, "Wrong email/password combination. Please try again.")
            return redirect("login")
        messages.warning(request, form.errors)
        return redirect("login")


class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect("login")
