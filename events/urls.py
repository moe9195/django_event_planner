from django.urls import path
from .views import (
	Login,
	Logout,
	Signup,
	home,
	EventDetailView,
	DashboardView,
	EventUpdateView,
	EventCreateView,
	MyEventsView,
	EventDeleteView,
	AllEventsView,
	EventBookView,
	BookedEventsView,
	EventHistoryView,
)
from django.contrib import admin

urlpatterns = [
	path('', home, name='home'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

	path('dashboard/', DashboardView, name='dashboard'),
	path('dashboard/eventlist', AllEventsView, name='event-list'),
	path('dashboard/create/', EventCreateView, name='event-create'),
	path('dashboard/detail/<int:event_id>/', EventDetailView, name='event-detail'),
	path('dashboard/detail/<int:event_id>/update/', EventUpdateView, name='event-update'),
	path('dashboard/detail/<int:event_id>/delete/', EventDeleteView, name='event-delete'),
	path('dashboard/detail/<int:event_id>/book/', EventBookView, name='event-book'),
	path('dashboard/myevents', MyEventsView, name='my-events'),
	path('dashboard/bookedevents', BookedEventsView, name='booked-events'),
	path('dashboard/history', EventHistoryView, name='event-history'),


]
