from django.urls import path
from . import views

urlpatterns = [
    # Common views
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # User views
    path('book-bed/', views.book_bed, name='book_bed'),
    path('booking-history/', views.booking_history, name='booking_history'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # Admin views
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-bed/', views.add_bed, name='add_bed'),
    path('edit-bed/<int:bed_id>/', views.edit_bed, name='edit_bed'),
    path('assign-bed/', views.assign_bed, name='assign_bed'),
    path('manage-booking/<int:booking_id>/', views.manage_booking, name='manage_booking'),
    path('icu-history/', views.icu_history, name='icu_history'),
]
