from django.urls import path
from .views import InvoiceExtractionView

app_name = 'api'  # Set your app name here

urlpatterns = [
    path('', InvoiceExtractionView.as_view(), name='extract_invoice'),
    # Add more URL patterns as needed
]
