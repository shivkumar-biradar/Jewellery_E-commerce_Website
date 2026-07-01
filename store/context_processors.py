from .models.cart import Cart
from .models.wishlist import Wishlist


def cart_and_wishlist(request):
    totalitem = 0
    wishlist_count = 0
    name = "Guest"


    if request.session.has_key("phone"):
        phone = request.session["phone"]

        totalitem = Cart.objects.filter(phone=phone).count()
        wishlist_count = Wishlist.objects.filter(phone=phone).count()


    return {
        "totalitem": totalitem,
        "wishlist_count": wishlist_count,
    }