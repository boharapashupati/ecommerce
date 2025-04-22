from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import stripe
import paypalrestsdk
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order
from .utils import send_payment_success_email, send_payment_failure_email

stripe.api_key = settings.STRIPE_SECRET_KEY
paypalrestsdk.configure({
    "mode": "sandbox" if settings.DEBUG else "live",
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class PaymentFormView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        
        context.update({
            'order': order,
            'user': self.request.user,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'paypal_client_id': settings.PAYPAL_CLIENT_ID
        })
        return context

class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method', 'stripe')
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            
            if payment_method == 'stripe':
                # Create Stripe payment intent
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),  # Convert to cents
                    currency='usd',
                    metadata={
                        'order_id': order.id,
                        'user_id': request.user.id
                    }
                )

                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    payment_method='stripe',
                    transaction_id=intent.id
                )

                serializer = self.get_serializer(payment)
                return Response({
                    'payment': serializer.data,
                    'client_secret': intent.client_secret
                }, status=status.HTTP_201_CREATED)

            elif payment_method == 'paypal':
                # Create PayPal order
                paypal_order = paypalrestsdk.Order({
                    "intent": "CAPTURE",
                    "purchase_units": [{
                        "amount": {
                            "currency_code": "USD",
                            "value": str(order.total_amount)
                        }
                    }]
                })

                if paypal_order.create():
                    # Create payment record
                    payment = Payment.objects.create(
                        order=order,
                        amount=order.total_amount,
                        payment_method='paypal',
                        transaction_id=paypal_order.id,
                        payment_details={'paypal_order': paypal_order.to_dict()}
                    )

                    serializer = self.get_serializer(payment)
                    return Response({
                        'payment': serializer.data,
                        'paypal_order_id': paypal_order.id
                    }, status=status.HTTP_201_CREATED)
                else:
                    raise Exception(paypal_order.error)

            elif payment_method == 'apple_pay':
                # Create Stripe payment intent for Apple Pay
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),
                    currency='usd',
                    payment_method_types=['card'],
                    metadata={
                        'order_id': order.id,
                        'user_id': request.user.id,
                        'payment_method': 'apple_pay'
                    }
                )

                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    payment_method='apple_pay',
                    transaction_id=intent.id
                )

                serializer = self.get_serializer(payment)
                return Response({
                    'payment': serializer.data,
                    'client_secret': intent.client_secret
                }, status=status.HTTP_201_CREATED)

            elif payment_method == 'google_pay':
                # Create Stripe payment intent for Google Pay
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),
                    currency='usd',
                    payment_method_types=['card'],
                    metadata={
                        'order_id': order.id,
                        'user_id': request.user.id,
                        'payment_method': 'google_pay'
                    }
                )

                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    payment_method='google_pay',
                    transaction_id=intent.id
                )

                serializer = self.get_serializer(payment)
                return Response({
                    'payment': serializer.data,
                    'client_secret': intent.client_secret
                }, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PaymentWebhookView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment = Payment.objects.get(transaction_id=payment_intent['id'])
            payment.status = 'completed'
            payment.save()

            # Update order status
            order = payment.order
            order.status = 'paid'
            order.save()

            # Send success email
            send_payment_success_email(order.user, order, payment)

        return Response({'status': 'success'})

class PayPalWebhookView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        event_type = request.data.get('event_type')
        
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            resource = request.data.get('resource')
            payment = Payment.objects.get(
                transaction_id=resource.get('order_id'),
                payment_method='paypal'
            )
            payment.status = 'completed'
            payment.save()

            # Update order status
            order = payment.order
            order.status = 'paid'
            order.save()

            # Send success email
            send_payment_success_email(order.user, order, payment)

        return Response({'status': 'success'})

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        payment = get_object_or_404(Payment, order=order, status='completed')
        
        context.update({
            'order': order,
            'payment': payment
        })
        return context

class PaymentFailureView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment_failure.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        error_message = self.request.GET.get('error', 'An error occurred during payment processing.')
        
        # Get the latest payment attempt
        payment = Payment.objects.filter(order=order).order_by('-created_at').first()
        
        # Send failure email
        if payment:
            send_payment_failure_email(order.user, order, payment, error_message)
        
        context.update({
            'order': order,
            'error_message': error_message,
            'payment': payment
        })
        return context

@login_required
def test_payment_emails(request):
    """Test view to send payment success and failure emails."""
    try:
        # Get the latest order for the current user
        order = Order.objects.filter(user=request.user).order_by('-created_at').first()
        if not order:
            return HttpResponse("No orders found for testing. Please create an order first.")
        
        # Get the latest payment for this order
        payment = Payment.objects.filter(order=order).order_by('-created_at').first()
        if not payment:
            return HttpResponse("No payments found for testing. Please make a payment first.")
        
        # Test success email
        send_payment_success_email(request.user, order, payment)
        
        # Test failure email
        send_payment_failure_email(
            request.user, 
            order, 
            payment, 
            "This is a test error message for payment failure notification."
        )
        
        return HttpResponse("Test emails sent successfully! Check your inbox.")
    except Exception as e:
        return HttpResponse(f"Error sending test emails: {str(e)}") 