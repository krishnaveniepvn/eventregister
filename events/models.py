from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import uuid
from datetime import datetime

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    venue = models.CharField(max_length=200)
    date = models.DateTimeField()
    capacity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events_created')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def available_seats(self):
        booked = self.registrations.filter(status='confirmed').count()
        return self.capacity - booked

class Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    ticket_number = models.CharField(max_length=50, unique=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.BooleanField(default=False)
    attended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.event.title}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        
        if not self.qr_code:
            self.generate_qr_code()
        
        super().save(*args, **kwargs)

    def generate_ticket_number(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"TKT-{timestamp}-{unique_id}"

    def generate_qr_code(self):
        qr_data = f"Event: {self.event.title}\n"
        qr_data += f"Ticket: {self.ticket_number}\n"
        qr_data += f"Attendee: {self.user.get_full_name() or self.user.email}\n"
        qr_data += f"Date: {self.event.date.strftime('%Y-%m-%d %H:%M')}\n"
        qr_data += f"Venue: {self.event.venue}"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        
        filename = f"qr_{self.ticket_number}.png"
        self.qr_code.save(filename, File(buffer), save=False)