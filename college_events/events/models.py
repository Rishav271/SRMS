from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    roll_no = models.CharField(max_length=30, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class Venue(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("cancelled", "Cancelled"),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="organized_events")
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # Added price
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(upload_to="event_images/", blank=True, null=True)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        return self.status == "published" and self.end_time > timezone.now()

    @property
    def spots_left(self):
        if self.max_attendees is None:
            return None
        return max(0, self.max_attendees - self.registrations.count())

from django.db import models
from django.contrib.auth.models import User

# models.py
class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    receipt = models.FileField(upload_to="receipts/", null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)  # <-- Add this if you want


    class Meta:
        unique_together = ("event", "user")
        ordering = ["-registered_at"]

    def __str__(self):
        return f"{self.user} -> {self.event}"

class Payment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} paid ₹{self.amount} for {self.event}"
