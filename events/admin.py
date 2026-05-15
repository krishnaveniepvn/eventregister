from django.contrib import admin
from .models import Event, Registration

class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'venue', 'capacity', 'available_seats', 'created_by', 'is_active']
    list_filter = ['is_active', 'date']
    search_fields = ['title', 'venue', 'description']
    date_hierarchy = 'date'
    raw_id_fields = ['created_by']

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'event', 'user', 'registration_date', 'status', 'attended']
    list_filter = ['status', 'attended', 'registration_date']
    search_fields = ['ticket_number', 'user__email', 'event__title']
    raw_id_fields = ['event', 'user']
    readonly_fields = ['ticket_number', 'qr_code']

admin.site.register(Event, EventAdmin)
admin.site.register(Registration, RegistrationAdmin)