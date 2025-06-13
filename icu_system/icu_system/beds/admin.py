from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ICUBed, ICUBooking, ICUHistory

@admin.register(ICUBed)
class ICUBedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'bed_type', 'is_available', 'price_per_day')
    list_filter = ('is_available', 'bed_type')
    search_fields = ('bed_number',)

@admin.register(ICUBooking)
class ICUBookingAdmin(admin.ModelAdmin):
    list_display = ('bed', 'patient_name', 'booked_by', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('patient_name', 'booked_by__username')

@admin.register(ICUHistory)
class ICUHistoryAdmin(admin.ModelAdmin):
    list_display = ('bed', 'patient_name', 'admitted_date', 'discharged_date')
    list_filter = ('admitted_date', 'discharged_date')
    search_fields = ('patient_name', 'bed__bed_number')
