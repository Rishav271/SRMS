from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Event, Registration
from .forms import EventForm
from .utils import generate_receipt
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

# -------------------- Home --------------------
def home(request):
    events = Event.objects.all().order_by("start_time")  # show upcoming events
    return render(request, "events/home.html", {"events": events})

# -------------------- Class-based Views --------------------
class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    paginate_by = 10

    def get_queryset(self):
        return Event.objects.filter(status="published").order_by("start_time")

class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

class EventDeleteView(DeleteView):
    model = Event
    template_name = "events/event_confirm_delete.html"
    success_url = "/"

# -------------------- Event Registration --------------------
@login_required
def register_for_event(request, pk):
    if request.method == "POST":
        event = get_object_or_404(Event, pk=pk, status="published")
        if event.max_attendees and event.registrations.count() >= event.max_attendees:
            return render(request, "events/event_full.html", {"event": event})
        
        # Register the user
        Registration.objects.get_or_create(event=event, user=request.user)
        
        # Redirect to registration success page
        return render(request, "events/registration_successful.html", {"event": event})
    
    # If GET request, redirect to event detail
    return redirect("events:event_detail", pk=pk)

@login_required
def unregister_from_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    Registration.objects.filter(event=event, user=request.user).delete()
    return redirect(reverse("events:event_detail", kwargs={"pk": pk}))

# -------------------- Authentication --------------------
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("events:register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("events:register")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Registration successful! Please login.")
        return redirect("events:login")

    return render(request, "events/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect("events:home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("events:login")
    return render(request, "events/login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("events:login")

# -------------------- Event Detail (function view) --------------------
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, "events/event_detail.html", {"event": event})

from django.contrib.auth.decorators import login_required
from .models import Registration

@login_required
def my_registrations(request):
    registrations = Registration.objects.filter(user=request.user).select_related('event')
    return render(request, "events/my_registrations.html", {"registrations": registrations})

import random
from .models import Payment

@login_required
def payment_page(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, "events/payment.html", {"event": event})


@login_required
def process_payment(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # Check if user already registered
    if Registration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "You are already registered.")
        return redirect("events:event_detail", pk=pk)

    if request.method == "POST":
        # Create registration
        registration = Registration.objects.create(user=request.user, event=event)

        # Save payment record (fake payment ID)
        import random
        payment_id = "PAY" + str(random.randint(100000, 999999))
        Payment.objects.create(
            user=request.user,
            event=event,
            amount=event.price,
            payment_id=payment_id,
            status="SUCCESS"
        )

        # Generate PDF receipt
        receipt_path = generate_receipt(request.user, event)
        registration.receipt = receipt_path  # Make sure Registration model has FileField or CharField
        registration.save()

        return render(request, "events/payment_success.html", {
            "event": event,
            "payment_id": payment_id,
            "receipt": registration.receipt.url if hasattr(registration.receipt, 'url') else registration.receipt
        })

    # If GET request, redirect to payment page
    return redirect("events:payment_page", pk=pk)