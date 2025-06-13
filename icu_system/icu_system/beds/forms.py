# from django import forms
# from .models import Booking
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm

# class BookingForm(forms.ModelForm):
#     class Meta:
#         model = Booking
#         fields = '__all__'
#         exclude = ['user', 'bed', 'status']

# class RegisterForm(UserCreationForm):
#     email = forms.EmailField()

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']
from django import forms
from .models import ICUBed, ICUBooking, ICUHistory


class ICUBedForm(forms.ModelForm):
    class Meta:
        model = ICUBed
        fields = ['bed_number', 'bed_type', 'is_available', 'description', 'price_per_day']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ICUBookingForm(forms.ModelForm):
    class Meta:
        model = ICUBooking
        fields = ['bed', 'patient_name', 'patient_age', 'patient_gender', 'contact_number', 'medical_condition', 'start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'medical_condition': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available beds for booking
        self.fields['bed'].queryset = ICUBed.objects.filter(is_available=True)


class AssignBedForm(forms.ModelForm):
    class Meta:
        model = ICUBooking
        fields = ['bed', 'patient_name', 'patient_age', 'patient_gender', 'contact_number', 'medical_condition', 'start_date', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'medical_condition': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Admin can see all beds
        self.fields['bed'].queryset = ICUBed.objects.all()


class ICUHistoryForm(forms.ModelForm):
    class Meta:
        model = ICUHistory
        fields = ['bed', 'patient_name', 'patient_age', 'patient_gender', 'admitted_date', 'discharged_date', 'treatment_details']
        widgets = {
            'admitted_date': forms.DateInput(attrs={'type': 'date'}),
            'discharged_date': forms.DateInput(attrs={'type': 'date'}),
            'treatment_details': forms.Textarea(attrs={'rows': 4}),
        }
