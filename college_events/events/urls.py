from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path('', views.home, name='home'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),

    path("event/create/", views.EventCreateView.as_view(), name="create"),
    path("event/<int:pk>/edit/", views.EventUpdateView.as_view(), name="edit"),
    path("event/<int:pk>/delete/", views.EventDeleteView.as_view(), name="delete"),

    path("event/<int:pk>/register/", views.register_for_event, name="event_register"),
    path("event/<int:pk>/unregister/", views.unregister_from_event, name="unregister"),

    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("my-registrations/", views.my_registrations, name="my_registrations"),

    # PAYMENT SYSTEM
    path("event/<int:pk>/payment/", views.payment_page, name="payment_page"),
    path("event/<int:pk>/process-payment/", views.process_payment, name="process_payment"),
]