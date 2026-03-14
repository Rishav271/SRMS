from django.contrib import admin
from django.utils import timezone

from .models import Profile, Venue, Event, Registration

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "roll_no", "department", "phone")

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "capacity")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer", "start_time", "end_time", "status")
    list_filter = ("status", "start_time")
    search_fields = ("title", "description")
    actions = ["publish", "cancel"]

    def publish(self, request, queryset):
        updated = queryset.update(status="published", published_at=timezone.now())
        self.message_user(request, f"{updated} event(s) published.")
    publish.short_description = "Publish selected events"

    def cancel(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} event(s) cancelled.")
    cancel.short_description = "Cancel selected events"

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "registered_at", "attended")

from django.contrib import admin
from .models import Event



