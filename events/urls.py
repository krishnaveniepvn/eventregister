from django.urls import path
from . import views

# No app_name to avoid namespace issues

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:pk>/register/', views.register_event, name='register_event'),
    path('registration/<int:pk>/success/', views.registration_success, name='registration_success'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    path('registration/<int:pk>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('ticket/<int:pk>/', views.download_ticket, name='download_ticket'),
    path('my-events/', views.events_created, name='events_created'),
    path('check-in/<int:pk>/', views.check_in, name='check_in'),
    # path('test/', views.test_urls, name='test_urls'),  # For debugging
]