from django.db import models

class Lead(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    referral = models.CharField(max_length=100, blank=True, null=True)
    consent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.phone}"

class Consultation(models.Model):
    URGENCY_CHOICES = [
        ('low', 'Low - General inquiry'),
        ('medium', 'Medium - Needs attention within 48 hours'),
        ('high', 'High - Needs attention within 24 hours'),
    ]
    
    AGE_CHOICES = [
        ('0-12', 'Child (0-12 years)'),
        ('13-19', 'Teen (13-19 years)'),
        ('20-35', 'Young Adult (20-35 years)'),
        ('36-50', 'Adult (36-50 years)'),
        ('51+', 'Senior (51+ years)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending - Awaiting doctor review'),  # New
        ('screening_form_sent', 'Screening Form Sent'),
        ('screening_completed', 'Screening Completed'),
        ('doctor_chat_scheduled', 'Doctor Chat Scheduled'),
        ('consultation_done', 'Consultation Done'),
        ('cancelled', 'Cancelled'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='consultations')

    symptoms = models.TextField()
    duration = models.CharField(max_length=100)
    age_range = models.CharField(max_length=50, choices=AGE_CHOICES)
    conditions = models.TextField(blank=True, null=True)

    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='low', blank=True, null=True)  # Made optional
    
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    
    # NEW FIELDS FOR DOCTOR RESPONSE
    doctor_response = models.TextField(blank=True, null=True)
    response_whatsapp_sent = models.BooleanField(default=False)
    response_email_sent = models.BooleanField(default=False)
    responded_by = models.CharField(max_length=100, blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consultation #{self.id} - {self.lead.name}"