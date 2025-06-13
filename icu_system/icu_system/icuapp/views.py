from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Bed, Booking
from .forms import BookingForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

def user_login(request):
    if request.method == 'POST':
        uname = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(username=uname, password=pwd)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    beds = Bed.objects.filter(is_available=True)
    my_bookings = Booking.objects.filter(user=request.user).order_by('-id')[:5]
    return render(request, 'dashboard.html', {'beds': beds, 'bookings': my_bookings})

@login_required
def book_bed(request, bed_id):
    bed = Bed.objects.get(id=bed_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.bed = bed
            booking.user = request.user
            booking.status = 'pending'
            booking.save()
            bed.is_available = False
            bed.save()
            return redirect('dashboard')
    else:
        form = BookingForm()
    return render(request, 'book_bed.html', {'form': form, 'bed': bed})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    all_beds = Bed.objects.all()
    all_bookings = Booking.objects.all()
    return render(request, 'admin_dashboard.html', {'beds': all_beds, 'bookings': all_bookings})
