from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        SELLER = 'SELLER', 'Seller'
        BUYER = 'BUYER', 'Buyer'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.BUYER
    )
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    def is_seller(self):
        return self.role == self.Role.SELLER
    
    def is_buyer(self):
        return self.role == self.Role.BUYER 