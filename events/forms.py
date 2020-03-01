from django import forms
from django.contrib.auth.models import User
from .models import Event, Booking
import datetime

class UserSignup(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email' ,'password']

        widgets={
        'password': forms.PasswordInput(),
        }

class UserLogin(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())

class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['owner']
        widgets = {
            'date':DateInput(),
            'time':TimeInput(),
        }
        labels = {
            "totalseats": "Available Seats"
        }
    def clean_date(self):
        date = self.cleaned_data['date']
        if date < datetime.date.today():
            raise forms.ValidationError("The date cannot be in the past!")
        return date

class BookForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['ticketnums']
        labels = {
            "ticketnums": "Amount"
        }
