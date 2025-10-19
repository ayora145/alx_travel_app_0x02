from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet
from . import views

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('initiate-payment/', views.initiate_payment, name='initiate-payment'),
    path('verify-payment/', views.verify_payment, name='verify-payment'),
]