from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from datetime import datetime, timedelta

from .models import Customer, Product, Appointment
from .forms import CustomerForm, ProductForm, AppointmentForm, PaymentUpdateForm


# Dashboard View
class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        # Get today's appointments
        today = timezone.now().date()
        today_appointments = Appointment.objects.filter(
            user=request.user,
            start_time__date=today
        ).order_by('start_time')
        
        # Get upcoming appointments (next 7 days)
        week_later = today + timedelta(days=7)
        upcoming_appointments = Appointment.objects.filter(
            user=request.user,
            start_time__date__gt=today,
            start_time__date__lte=week_later
        ).order_by('start_time')
        
        # Get pending payments
        pending_payments = Appointment.objects.filter(
            user=request.user,
            payment_status='PENDING'
        ).order_by('-start_time')
        
        # Get total number of customers
        total_customers = Customer.objects.filter(user=request.user).count()
        
        context = {
            'today_appointments': today_appointments,
            'upcoming_appointments': upcoming_appointments,
            'pending_payments': pending_payments,
            'total_customers': total_customers,
        }
        return render(request, 'core/dashboard.html', context)


# Customer Views
class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'core/customers/list.html'
    context_object_name = 'customers'
    
    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user).order_by('-created_at')


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'core/customers/detail.html'
    context_object_name = 'customer'
    
    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = Appointment.objects.filter(
            customer=self.object
        ).order_by('-start_time')
        return context


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'core/customers/create.html'
    success_url = reverse_lazy('customer-list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'core/customers/update.html'
    
    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('customer-detail', kwargs={'pk': self.object.pk})


# Product Views
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'core/products/list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.filter(user=self.request.user).order_by('-created_at')


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'core/products/create.html'
    success_url = reverse_lazy('product-list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'core/products/update.html'
    success_url = reverse_lazy('product-list')
    
    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)


# Appointment Views
class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'core/appointments/list.html'
    context_object_name = 'appointments'
    
    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).order_by('-start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Count today's appointments
        context['today_appointments_count'] = Appointment.objects.filter(
            user=self.request.user,
            start_time__date=today
        ).count()
        
        # Count pending payments
        context['pending_payments_count'] = Appointment.objects.filter(
            user=self.request.user,
            payment_status='PENDING'
        ).count()
        
        context['today'] = today
        return context

class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'core/appointments/create.html'
    success_url = reverse_lazy('appointment-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter customers and products to only show those belonging to the user
        form.fields['customer'].queryset = Customer.objects.filter(user=self.request.user)
        form.fields['product'].queryset = Product.objects.filter(user=self.request.user)
        return form
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = 'core/appointments/detail.html'
    context_object_name = 'appointment'
    
    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user)


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'core/appointments/update.html'
    
    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter customers and products to only show those belonging to the user
        form.fields['customer'].queryset = Customer.objects.filter(user=self.request.user)
        form.fields['product'].queryset = Product.objects.filter(user=self.request.user)
        return form
    
    def get_success_url(self):
        return reverse_lazy('appointment-detail', kwargs={'pk': self.object.pk})
    
@method_decorator(login_required, name='dispatch')
class AppointmentCancelView(View):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
        appointment.payment_status = 'CANCELED'
        appointment.save()
        messages.success(request, f'Appointment with {appointment.customer.name} has been canceled.')
        return redirect('appointment-list')


# Calendar View
class CalendarView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'core/appointments/calendar.html')

    def post(self, request):
        # Endpoint for getting appointments in a date range (for calendar)
        start_date = request.POST.get('start')
        end_date = request.POST.get('end')
        
        try:
            # Handle ISO format dates that FullCalendar sends
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Query appointments in date range
            appointments = Appointment.objects.filter(
                user=request.user,
                start_time__gte=start_date,
                end_time__lte=end_date
            )
            
            events = []
            for appointment in appointments:
                events.append({
                    'id': appointment.id,
                    'title': f"{appointment.customer.name}",
                    'start': appointment.start_time.isoformat(),
                    'end': appointment.end_time.isoformat(),
                    'url': str(reverse_lazy('appointment-detail', kwargs={'pk': appointment.pk})),
                    'status': appointment.payment_status
                })
            
            return JsonResponse(events, safe=False)
        except Exception as e:
            import traceback
            print(f"Calendar error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


# Payment Status Update
@method_decorator(login_required, name='dispatch')
class PaymentStatusUpdateView(View):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
        form = PaymentUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment-detail', pk=pk)
        
        # If form is not valid, return to the appointment detail page with errors
        return render(request, 'core/appointments/detail.html', {
            'appointment': appointment,
            'payment_form': form
        })


# Search functionality (optional for MVP)
@method_decorator(login_required, name='dispatch')
class SearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        
        if query:
            customers = Customer.objects.filter(
                Q(name__icontains=query) | 
                Q(email__icontains=query) | 
                Q(phone__icontains=query),
                user=request.user
            )
            
            appointments = Appointment.objects.filter(
                Q(customer__name__icontains=query) |
                Q(notes__icontains=query),
                user=request.user
            )
        else:
            customers = Customer.objects.none()
            appointments = Appointment.objects.none()
        
        return render(request, 'core/search_results.html', {
            'query': query,
            'customers': customers,
            'appointments': appointments
        })