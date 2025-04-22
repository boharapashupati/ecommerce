from django.urls import path
from .views import (
    CartItemListView, CartItemDetailView,
    OrderListView, OrderDetailView
)

urlpatterns = [
    # Cart URLs
    path('cart/', CartItemListView.as_view(), name='cart-list'),
    path('cart/<int:pk>/', CartItemDetailView.as_view(), name='cart-detail'),
    
    # Order URLs
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
] 