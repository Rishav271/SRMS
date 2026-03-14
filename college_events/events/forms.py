from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "venue", "start_time", "end_time", "max_attendees", "price"]


class RegistrationForm(forms.Form):
    # simple confirm form (e.g. a checkbox)
    confirm = forms.BooleanField(label="Confirm registration")
