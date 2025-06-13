from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ICUBed(models.Model):
    BED_TYPES = [
        ('general', 'General ICU'),
        ('cardiac', 'Cardiac ICU'),
        ('neonatal', 'Neonatal ICU'),
        ('pediatric', 'Pediatric ICU'),
        ('surgical', 'Surgical ICU'),
    ]
    
    bed_number = models.CharField(max_length=10, unique=True)
    bed_type = models.CharField(max_length=20, choices=BED_TYPES)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.bed_number} - {self.get_bed_type_display()}"
    
    def toggle_availability(self):
        self.is_available = not self.is_available
        self.save()


class ICUBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    bed = models.ForeignKey(ICUBed, on_delete=models.CASCADE, related_name='bookings')
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    patient_name = models.CharField(max_length=100)
    patient_age = models.PositiveIntegerField()
    patient_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=15)
    medical_condition = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient_name} - {self.bed.bed_number}"
    
    def save(self, *args, **kwargs):
        # When booking is confirmed, mark the bed as unavailable
        if self.status == 'confirmed' and self.bed.is_available:
            self.bed.is_available = False
            self.bed.save()
        
        # When booking is cancelled or completed, mark the bed as available
        elif self.status in ['cancelled', 'completed'] and not self.bed.is_available:
            self.bed.is_available = True
            self.bed.save()
            
            # If completed, create a history record
            if self.status == 'completed' and self.end_date:
                ICUHistory.objects.create(
                    bed=self.bed,
                    patient_name=self.patient_name,
                    patient_age=self.patient_age,
                    patient_gender=self.patient_gender,
                    admitted_date=self.start_date,
                    discharged_date=self.end_date,
                    treatment_details=self.medical_condition
                )
                
        super().save(*args, **kwargs)


class ICUHistory(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    bed = models.ForeignKey(ICUBed, on_delete=models.CASCADE, related_name='history')
    patient_name = models.CharField(max_length=100)
    patient_age = models.PositiveIntegerField()
    patient_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    admitted_date = models.DateField()
    discharged_date = models.DateField(null=True, blank=True)
    treatment_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient_name} - {self.bed.bed_number} - {self.admitted_date}"
    
    class Meta:
        verbose_name_plural = "ICU Histories"
