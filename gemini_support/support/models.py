from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customer')

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"


class Ticket(models.Model):
    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('In Process', 'In Process'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    )

    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    )

    CATEGORY_CHOICES = [
        ('Technical', 'Technical'),
        ('Non-Technical', 'Non-Technical'),
        ('Functional', 'Functional'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Technical')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    attachment = models.FileField(upload_to='ticket_attachments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject} ({self.status})"


class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reply by {self.responder.username} on Ticket #{self.ticket.id}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Process', 'In Process'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Open')
    attachment = models.FileField(upload_to='ticket_attachments/', blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} ({self.user.username})"