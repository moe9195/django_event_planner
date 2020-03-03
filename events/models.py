from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from annoying.fields import AutoOneToOneField
from PIL import Image

def validate_nonzero(value):
    if value == 0:
        raise ValidationError(
            _('Quantity %(value)s is not allowed'),
            params={'value': value},
        )

class Event(models.Model):
    title = models.CharField(max_length=120)
    owner = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    description = models.TextField(max_length=10000)
    location = models.TextField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    price = models.IntegerField(default=None, null=True)
    totalseats = models.PositiveIntegerField(validators=[validate_nonzero])

    def seats_booked(self):
        return sum(self.bookings.all().values_list('ticketnums', flat=True))
    def seats_left(self):
        return self.totalseats - self.seats_booked()
    def is_fully_booked(self):
        return (self.seats_left() == 0)

class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    ticketnums = models.PositiveIntegerField(validators=[validate_nonzero])
    booking_date = models.DateField(auto_now_add=True)
    booking_time = models.TimeField(auto_now_add=True)

    def price_paid(self):
        return self.ticketnums * self.event.price

class Profile(models.Model):
    user = AutoOneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    follows = models.ManyToManyField('Profile', related_name='followed_by', symmetrical=False, default=None)
    profile_picture = models.ImageField(default='noimage.png')
    bio = models.TextField(max_length=500, blank=True, default=" ")

    def resize_image(self):
        return self.resize((250,250), Image.ANTIALIAS)

    def __str__(self):
        return 'Profile of user: {}'.format(self.user.username)
