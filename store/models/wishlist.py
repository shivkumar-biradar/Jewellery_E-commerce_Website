from django.db import models
from .product import Product



class Wishlist(models.Model):
    phone = models.CharField(max_length=15) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} - {self.product.name}"
