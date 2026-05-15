from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone  # Add this import
from .models import Event, Registration
from .forms import EventForm, RegistrationForm

# Home page - redirects to event list
def home(request):
    return redirect('event_list')

# Display list of upcoming events
def event_list(request):
    events = Event.objects.filter(
        date__gte=timezone.now(),
        is_active=True
    ).order_by('date')
    
    context = {
        'events': events,
        'now': timezone.now(),
    }
    return render(request, 'events/event_list.html', context)

# Display event details
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    
    user_registered = False
    if request.user.is_authenticated:
        user_registered = Registration.objects.filter(
            event=event, 
            user=request.user,
            status__in=['pending', 'confirmed']
        ).exists()
    
    context = {
        'event': event,
        'user_registered': user_registered,
        'now': timezone.now(),
    }
    return render(request, 'events/event_detail.html', context)

# Create a new event
@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event'})

# Register for an event
@login_required
def register_event(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    
    if event.available_seats <= 0:
        messages.error(request, 'Sorry, this event is full.')
        return redirect('event_detail', pk=event.pk)
    
    existing_registration = Registration.objects.filter(
        event=event, 
        user=request.user,
        status__in=['pending', 'confirmed']
    ).first()
    
    if existing_registration:
        messages.warning(request, 'You are already registered for this event.')
        return redirect('my_registrations')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = Registration.objects.create(
                event=event,
                user=request.user,
                status='confirmed'
            )
            
            send_registration_email(request, registration)
            
            messages.success(request, f'Successfully registered for {event.title}! Check your email for the ticket.')
            return redirect('registration_success', pk=registration.pk)
    else:
        form = RegistrationForm()
    
    context = {
        'form': form,
        'event': event,
        'now': timezone.now(),
    }
    return render(request, 'events/register_event.html', context)

# Send registration confirmation email
def send_registration_email(request, registration):
    subject = f'Registration Confirmation - {registration.event.title}'
    
    message = f"""
    Dear {registration.user.get_full_name() or registration.user.email},
    
    Thank you for registering for {registration.event.title}!
    
    Event Details:
    --------------
    Event: {registration.event.title}
    Date: {registration.event.date.strftime('%B %d, %Y at %I:%M %p')}
    Venue: {registration.event.venue}
    Ticket Number: {registration.ticket_number}
    
    Your QR code is attached to this email. Please present it at the venue for check-in.
    
    We look forward to seeing you at the event!
    
    Best regards,
    Event Management Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [registration.user.email],
        fail_silently=False,
    )

# Registration success page
@login_required
def registration_success(request, pk):
    registration = get_object_or_404(Registration, pk=pk, user=request.user)
    
    context = {
        'registration': registration,
        'now': timezone.now(),
    }
    return render(request, 'events/registration_success.html', context)

# Display user's registrations
@login_required
def my_registrations(request):
    registrations = Registration.objects.filter(
        user=request.user
    ).select_related('event').order_by('-registration_date')
    
    upcoming_count = registrations.filter(
        event__date__gte=timezone.now(),
        status__in=['confirmed', 'pending']
    ).count()
    
    confirmed_count = registrations.filter(status='confirmed').count()
    pending_count = registrations.filter(status='pending').count()
    attended_count = registrations.filter(status='attended').count()
    cancelled_count = registrations.filter(status='cancelled').count()
    
    context = {
        'registrations': registrations,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
        'attended_count': attended_count,
        'cancelled_count': cancelled_count,
        'upcoming_count': upcoming_count,
        'now': timezone.now(),
    }
    return render(request, 'events/my_registrations.html', context)

# Cancel a registration
@login_required
def cancel_registration(request, pk):
    registration = get_object_or_404(Registration, pk=pk, user=request.user)
    
    if registration.status in ['pending', 'confirmed']:
        registration.status = 'cancelled'
        registration.save()
        
        subject = f'Registration Cancelled - {registration.event.title}'
        message = f"""
        Dear {registration.user.get_full_name() or registration.user.email},
        
        Your registration for {registration.event.title} has been cancelled.
        
        If this was a mistake, please register again through our website.
        
        Best regards,
        Event Management Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [registration.user.email],
            fail_silently=False,
        )
        
        messages.success(request, 'Registration cancelled successfully.')
    
    return redirect('my_registrations')

# Download/view ticket
@login_required
def download_ticket(request, pk):
    registration = get_object_or_404(Registration, pk=pk, user=request.user)
    
    context = {
        'registration': registration,
        'now': timezone.now(),
    }
    return render(request, 'events/ticket.html', context)

# Show events created by the current user
@login_required
def events_created(request):
    events = Event.objects.filter(created_by=request.user).order_by('-created_at')
    
    upcoming_events = events.filter(date__gte=timezone.now()).count()
    total_registrations = sum(event.registrations.count() for event in events)
    active_events = events.filter(is_active=True).count()
    
    for event in events:
        event.total_registrations = event.registrations.count()
        event.confirmed_registrations = event.registrations.filter(status='confirmed').count()
        event.attended_registrations = event.registrations.filter(status='attended').count()
    
    context = {
        'events': events,
        'total_registrations': total_registrations,
        'active_events': active_events,
        'upcoming_events': upcoming_events,
        'now': timezone.now(),
    }
    return render(request, 'events/events_created.html', context)

# Check-in attendees (staff only)
@login_required
def check_in(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('event_list')
    
    registration = get_object_or_404(Registration, pk=pk)
    
    if request.method == 'POST' and registration.status == 'confirmed':
        registration.status = 'attended'
        registration.attended = True
        registration.save()
        messages.success(request, f'Checked in: {registration.user.get_full_name() or registration.user.email}')
        return redirect('event_detail', pk=registration.event.pk)
    
    context = {
        'registration': registration,
        'now': timezone.now(),
    }
    return render(request, 'events/check_in.html', context)