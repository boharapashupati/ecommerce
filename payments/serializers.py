from rest_framework import serializers
from .models import Payment
from orders.serializers import OrderSerializer

class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'order', 'order_id', 'amount', 'status', 'payment_method', 'transaction_id', 'created_at')
        read_only_fields = ('id', 'status', 'transaction_id', 'created_at') 