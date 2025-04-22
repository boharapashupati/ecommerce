from django.urls import path
from .views import (
    PaymentCreateView, PaymentWebhookView,
    PaymentListView, PaymentDetailView,
    PaymentFormView, PayPalWebhookView,
    PaymentSuccessView, PaymentFailureView,test_payment_emails
)

urlpatterns = [
    path('create/', PaymentCreateView.as_view(), name='payment-create'),
    path('webhook/stripe/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('webhook/paypal/', PayPalWebhookView.as_view(), name='paypal-webhook'),
    path('list/', PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('form/<int:order_id>/', PaymentFormView.as_view(), name='payment-form'),
    path('<int:order_id>/success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('<int:order_id>/failure/', PaymentFailureView.as_view(), name='payment-failure'),
    path('test-emails/', test_payment_emails, name='test-payment-emails'),
] 