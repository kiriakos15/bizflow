from django import forms
from django.forms import DateTimeInput
from .models import Customer, Product, Appointment


class DateTimePickerInput(DateTimeInput):
    """Custom datetime input widget with HTML5 datetime-local input type."""
    input_type = 'datetime-local'


class CustomerForm(forms.ModelForm):
    """Form for adding and updating customers."""
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-md', 'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    """Form for adding and updating products/services."""
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-md', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-md', 'step': '0.01'}),
        }


class AppointmentForm(forms.ModelForm):
    """Form for creating and updating appointments."""
    class Meta:
        model = Appointment
        fields = ['customer', 'product', 'start_time', 'end_time', 'notes', 'payment_status']
        widgets = {
            'customer': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'product': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'start_time': DateTimePickerInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'end_time': DateTimePickerInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-md', 'rows': 3}),
            'payment_status': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
        }


class PaymentUpdateForm(forms.ModelForm):
    """Simple form for updating appointment payment status."""
    class Meta:
        model = Appointment
        fields = ['payment_status']
        widgets = {
            'payment_status': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
        }