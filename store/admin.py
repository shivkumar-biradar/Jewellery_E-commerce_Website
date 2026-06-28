from django.contrib import admin
from .models.product import Product
from .models.category import Category
from .models.customer import Customer
from .models.cart import Cart
from .models.order import OrderDetail

class AdminProduct(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'category', 'description']

class AdminCustomer(admin.ModelAdmin):
    # Fixed: Changed 'phone' to 'mobile' to match your Customer model fields
    list_display = ['id', 'name', 'mobile']

class AdminCart(admin.ModelAdmin):
    list_display = ['id', 'phone', 'product', 'image', 'price']

class AdminOrder(admin.ModelAdmin):
    list_display = ['id','user','product_name','qty','image','price','status','ordered_date']


admin.site.register(Product, AdminProduct)
admin.site.register(Category)
admin.site.register(Customer, AdminCustomer)
admin.site.register(Cart,AdminCart)
admin.site.register(OrderDetail,AdminOrder)
