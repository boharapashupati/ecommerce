from rest_framework import serializers
from .models import CartItem, Order, OrderItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'total_price')
        read_only_fields = ('id', 'total_price')

    def get_total_price(self, obj):
        return obj.quantity * obj.product.price

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'items', 'status', 'total_amount', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'total_amount', 'created_at', 'updated_at')

    def get_total_amount(self, obj):
        return sum(item.quantity * item.price for item in obj.items.all()) 