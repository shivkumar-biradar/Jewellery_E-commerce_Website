from django.contrib import admin
from django.urls import path
# from .views import home, signup
from store import views

urlpatterns = [
    # Fixed: Added name='homepage' to the home view path
    path('', views.home, name='homepage'),
    path('search/', views.search_products, name='search_products'),
    path('signup/',views.Signup.as_view(), name='signup'),
    path('login/',views.Login.as_view(), name='login'),
    path('product-detail/<int:pk>/',views.productdetail,name='product-detail'),
    path('logout/',views.Logout.as_view(), name='logout'),
    path('add_to_cart/',views.add_to_cart, name='add_to_cart'),
    path('show_cart/',views.show_cart, name='show_cart'),
    path('plus_cart/',views.plus_cart, name='plus_cart'),
    path('minus_cart/', views.minus_cart, name='minus_cart'),
    path('remove_cart/', views.remove_cart, name='remove_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-verify/', views.payment_verify, name='payment_verify'),
    path('download-invoice/<int:order_id>/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('order/', views.order, name='order'),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.show_wishlist, name='show_wishlist'),
    path('buy-now/<int:prod_id>/', views.buy_now, name='buy_now'),
    path('payment-verify/', views.payment_verify, name='payment_verify')


]
