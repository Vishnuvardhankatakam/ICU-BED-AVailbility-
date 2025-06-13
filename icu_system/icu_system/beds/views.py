from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .models import ICUBed, ICUBooking, ICUHistory
from .forms import ICUBedForm, ICUBookingForm, AssignBedForm, ICUHistoryForm


# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff or user.is_superuser


# Common views
@login_required
def dashboard(request):
    """Main dashboard that redirects to appropriate view based on user role"""
    if is_admin(request.user):
        return redirect('admin_dashboard')
    
    available_beds = ICUBed.objects.filter(is_available=True)
    user_bookings = ICUBooking.objects.filter(booked_by=request.user).order_by('-booking_date')[:5]
    
    context = {
        'available_beds': available_beds,
        'recent_bookings': user_bookings,
    }
    return render(request, 'beds/dashboard.html', context)


# User views
@login_required
def book_bed(request):
    """Allow regular users to book an available ICU bed"""
    if request.method == 'POST':
        form = ICUBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.booked_by = request.user
            
            # If the user is an admin, auto-confirm the booking
            if is_admin(request.user):
                booking.status = 'confirmed'
            
            booking.save()
            messages.success(request, 'Bed booking request submitted successfully!')
            return redirect('dashboard')
    else:
        form = ICUBookingForm()
    
    context = {
        'form': form,
        'available_beds': ICUBed.objects.filter(is_available=True)
    }
    return render(request, 'beds/book_bed.html', context)


@login_required
def booking_history(request):
    """Show booking history for the current user"""
    bookings = ICUBooking.objects.filter(booked_by=request.user).order_by('-booking_date')
    return render(request, 'beds/booking_history.html', {'bookings': bookings})


@login_required
def cancel_booking(request, booking_id):
    """Allow users to cancel their pending bookings"""
    booking = get_object_or_404(ICUBooking, id=booking_id)
    
    # Check if the booking belongs to the current user or if user is admin
    if booking.booked_by != request.user and not is_admin(request.user):
        messages.error(request, 'You do not have permission to cancel this booking.')
        return redirect('booking_history')
    
    # Only pending or confirmed bookings can be cancelled
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, f'Cannot cancel a booking with status "{booking.get_status_display()}".')
        return redirect('booking_history')
    
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, 'Booking cancelled successfully.')
    
    if is_admin(request.user):
        return redirect('admin_dashboard')
    return redirect('booking_history')


# Admin views
@login_required
def admin_dashboard(request):
    """Admin dashboard with overview of ICU bed status"""
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('dashboard')
    
    total_beds = ICUBed.objects.count()
    available_beds = ICUBed.objects.filter(is_available=True).count()
    occupied_beds = total_beds - available_beds
    
    pending_bookings = ICUBooking.objects.filter(status='pending').count()
    recent_bookings = ICUBooking.objects.order_by('-booking_date')[:10]
    
    context = {
        'total_beds': total_beds,
        'available_beds': available_beds,
        'occupied_beds': occupied_beds,
        'pending_bookings': pending_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'beds/admin_dashboard.html', context)


@login_required
def add_bed(request):
    """Allow admins to add new ICU beds"""
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to add ICU beds.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ICUBedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'ICU bed added successfully!')
            return redirect('admin_dashboard')
    else:
        form = ICUBedForm()
    
    return render(request, 'beds/add_bed.html', {'form': form})


@login_required
def edit_bed(request, bed_id):
    """Allow admins to edit existing ICU beds"""
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to edit ICU beds.')
        return redirect('dashboard')
    
    bed = get_object_or_404(ICUBed, id=bed_id)
    
    if request.method == 'POST':
        form = ICUBedForm(request.POST, instance=bed)
        if form.is_valid():
            form.save()
            messages.success(request, 'ICU bed updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = ICUBedForm(instance=bed)
    
    return render(request, 'beds/add_bed.html', {'form': form, 'is_edit': True})


@login_required
def assign_bed(request):
    """Allow admins to directly assign ICU beds to patients"""
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to assign ICU beds.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AssignBedForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.booked_by = request.user
            booking.save()
            messages.success(request, 'ICU bed assigned successfully!')
            return redirect('admin_dashboard')
    else:
        form = AssignBedForm(initial={'status': 'confirmed'})
    
    return render(request, 'beds/assign_bed.html', {'form': form})


@login_required
def manage_booking(request, booking_id):
    """Allow admins to manage bookings (confirm, cancel, complete)"""
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to manage bookings.')
        return redirect('dashboard')
    
    booking = get_object_or_404(ICUBooking, id=booking_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm':
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, 'Booking confirmed successfully.')
        
        elif action == 'cancel':
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, 'Booking cancelled successfully.')
        
        elif action == 'complete':
            booking.status = 'completed'
            booking.end_date = date.today()
            booking.save()
            messages.success(request, 'Booking marked as completed successfully.')
        
        return redirect('admin_dashboard')
    
    return render(request, 'beds/manage_booking.html', {'booking': booking})


@login_required
def icu_history(request):
    """View ICU usage history"""
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to view ICU history.')
        return redirect('dashboard')
    
    histories = ICUHistory.objects.all().order_by('-discharged_date')
    return render(request, 'beds/icu_history.html', {'histories': histories})

