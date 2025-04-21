from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='core/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<int:pk>/update/', views.CustomerUpdateView.as_view(), name='customer-update'),
    
    # Products/Services
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    
    # Appointments
    path('appointments/', views.AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/calendar/', views.CalendarView.as_view(), name='appointment-calendar'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/create/', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('appointments/<int:pk>/update/', views.AppointmentUpdateView.as_view(), name='appointment-update'),
    path('appointments/<int:pk>/payment-status/', views.PaymentStatusUpdateView.as_view(), name='payment-status-update'),
    path('appointments/<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='appointment-cancel'),
    
    # Search
    path('search/', views.SearchView.as_view(), name='search'),
]