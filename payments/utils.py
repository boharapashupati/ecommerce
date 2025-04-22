from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from datetime import datetime

def send_payment_success_email(user, order, payment):
    """Send a success email to the user after a successful payment."""
    context = {
        'user': user,
        'order': order,
        'payment': payment,
        'order_url': settings.SITE_URL + reverse('order-detail', kwargs={'pk': order.id}),
        'current_year': datetime.now().year
    }
    
    html_message = render_to_string('payments/emails/payment_success_email.html', context)
    
    send_mail(
        subject='Payment Successful - Order #{}'.format(order.id),
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_payment_failure_email(user, order, payment, error_message):
    """Send a failure email to the user after a failed payment."""
    context = {
        'user': user,
        'order': order,
        'payment': payment,
        'error_message': error_message,
        'retry_url': settings.SITE_URL + reverse('payment-form', kwargs={'order_id': order.id}),
        'current_year': datetime.now().year
    }
    
    html_message = render_to_string('payments/emails/payment_failure_email.html', context)
    
    send_mail(
        subject='Payment Failed - Order #{}'.format(order.id),
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    ) 