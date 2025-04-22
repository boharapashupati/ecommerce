from django.db import models
from django.conf import settings
from products.models import Product

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Cart  {self.id} for user {self.user.username}"
    
# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')

#     quantity = models.PositiveIntegerField(default=1)

#     def __str__(self):
#         return f"{self.quantity}*{self.product.name}" 