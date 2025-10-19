from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from .tasks import send_payment_confirmation_email


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

import requests
import uuid
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment

@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        data = request.POST
        amount = data.get('amount')
        email = data.get('email')

        # Validate required fields
        if not amount or not email:
            return JsonResponse({"error": "Amount and email are required"}, status=400)

        booking_reference = str(uuid.uuid4())

        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": email,
            "tx_ref": booking_reference,
            "callback_url": "http://127.0.0.1:8000/api/verify-payment/",
            "return_url": "http://127.0.0.1:8000/payment-success/",
            "customization[title]": "Travel Booking Payment",
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
            chapa_response = response.json()

            if response.status_code == 200 and chapa_response.get('status') == 'success':
                Payment.objects.create(
                    booking_reference=booking_reference,
                    amount=amount,
                    email=email,
                    transaction_id=chapa_response['data']['tx_ref'],
                    status='Pending'
                )
                return JsonResponse({"checkout_url": chapa_response['data']['checkout_url']})
            else:
                # For testing purposes, create a mock successful response
                if settings.DEBUG:
                    Payment.objects.create(
                        booking_reference=booking_reference,
                        amount=amount,
                        email=email,
                        transaction_id=booking_reference,
                        status='Pending'
                    )
                    return JsonResponse({
                        "checkout_url": f"http://127.0.0.1:8000/mock-payment/{booking_reference}/",
                        "message": "Mock payment created for testing",
                        "booking_reference": booking_reference
                    })
                return JsonResponse({"error": "Payment initiation failed", "details": chapa_response}, status=400)
        except Exception as e:
            return JsonResponse({"error": "Payment service unavailable", "details": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def verify_payment(request):
    if request.method == 'GET':
        tx_ref = request.GET.get('tx_ref')

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        }

        response = requests.get(f"https://api.chapa.co/v1/transaction/verify/{tx_ref}", headers=headers)
        chapa_response = response.json()

        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Transaction not found"}, status=404)

        if chapa_response.get('status') == 'success' and chapa_response['data']['status'] == 'success':
            payment.status = 'Completed'
            payment.save()
            # trigger email here (Celery)
            send_payment_confirmation_email.delay(payment.email, payment.booking_reference)
            return JsonResponse({"message": "Payment verified successfully"})
        else:
            payment.status = 'Failed'
            payment.save()
            return JsonResponse({"message": "Payment failed or incomplete"})

    return JsonResponse({"error": "Invalid request method"}, status=405)
