from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import ICUBed, ICUBooking, ICUHistory


class ICUBedModelTests(TestCase):
    def setUp(self):
        self.bed = ICUBed.objects.create(
            bed_number='ICU-001',
            bed_type='general',
            is_available=True,
            price_per_day=5000
        )

    def test_bed_creation(self):
        self.assertEqual(self.bed.bed_number, 'ICU-001')
        self.assertTrue(self.bed.is_available)

    def test_toggle_availability(self):
        self.assertTrue(self.bed.is_available)
        self.bed.toggle_availability()
        self.assertFalse(self.bed.is_available)
        self.bed.toggle_availability()
        self.assertTrue(self.bed.is_available)


class ICUBookingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.bed = ICUBed.objects.create(
            bed_number='ICU-001',
            bed_type='general',
            is_available=True,
            price_per_day=5000
        )
        self.booking = ICUBooking.objects.create(
            bed=self.bed,
            booked_by=self.user,
            patient_name='Test Patient',
            patient_age=45,
            patient_gender='male',
            contact_number='1234567890',
            medical_condition='Test condition',
            start_date='2023-07-01',
            status='pending'
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.patient_name, 'Test Patient')
        self.assertEqual(self.booking.status, 'pending')
        self.assertTrue(self.bed.is_available)  # Bed should still be available while pending

    def test_booking_confirmation(self):
        self.booking.status = 'confirmed'
        self.booking.save()
        
        # Refresh bed from database
        self.bed.refresh_from_db()
        self.assertFalse(self.bed.is_available)  # Bed should now be unavailable

    def test_booking_completion(self):
        # First confirm the booking
        self.booking.status = 'confirmed'
        self.booking.save()
        
        # Then complete it
        self.booking.status = 'completed'
        self.booking.end_date = '2023-07-10'
        self.booking.save()
        
        # Refresh bed from database
        self.bed.refresh_from_db()
        self.assertTrue(self.bed.is_available)  # Bed should be available again
        
        # Check if history was created
        history = ICUHistory.objects.filter(patient_name='Test Patient').first()
        self.assertIsNotNone(history)
        self.assertEqual(history.admitted_date.strftime('%Y-%m-%d'), '2023-07-01')
        self.assertEqual(history.discharged_date.strftime('%Y-%m-%d'), '2023-07-10')
