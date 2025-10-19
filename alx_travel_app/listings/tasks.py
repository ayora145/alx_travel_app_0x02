from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_payment_confirmation_email(email, booking_reference):
    subject = "Payment Confirmation - Travel Booking"
    message = f"Your payment for booking reference {booking_reference} has been confirmed."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )