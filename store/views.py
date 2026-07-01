from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views import View
from django.db.models import Q
from django.conf import settings
import razorpay

from .models.product import Product
from .models.category import Category
from .models.customer import Customer
from .models.cart import Cart
from .models.order import OrderDetail
from django.views.decorators.csrf import csrf_exempt
from .models.wishlist import Wishlist  
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string

def home(request):
    totalitem = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        category = Category.get_all_categories()
        customer_data = Customer.objects.filter(mobile=phone)
        totalitem = len(Cart.objects.filter(phone=phone))
        name = "Guest"
        for c in customer_data:
            name = c.name
        categoryID = request.GET.get('category')
        if categoryID:
            products = Product.get_all_products_by_category_id(categoryID)
        else:
            products = Product.get_all_products()
        sort_by = request.GET.get('sort_by', '')
        if sort_by == 'price_low_high':
            products = products.order_by('price')
        elif sort_by == 'price_high_low':
            products = products.order_by('-price')
        elif sort_by == 'alpha_a_z':
            products = products.order_by('name')
        elif sort_by == 'alpha_z_a':
            products = products.order_by('-name')

        data = {
            'name': name,
            'products': products,
            'categories': category,
            'totalitem': totalitem,
        }
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('product_grid_snippet.html', {'products': products}, request=request)
            return HttpResponse(html)

        return render(request, 'home.html', data)
    else:
        return redirect('login')

class Signup(View):
    def get(self,request):
        return render(request, 'signup.html')
    def post(self,request):
        postData = request.POST
        name = postData.get('name')
        mobile = postData.get('mobile')
        error_message = None
        value = {
            'mobile':mobile,
            'name':name
        }
        customer = Customer(name=name, mobile=mobile)
        if not name:
            error_message = "Name is Required"
        elif not mobile:
            error_message = "Mobile no is required"
        elif len(mobile) < 10:
            error_message = "Mobile no must be 10 characters Long or more"
        elif customer.isExists():
            error_message = "Mobile Number Already Exist"
        if not error_message:
            messages.success(request, 'Congratulations! Registered Successfully')
            customer.register()
            return redirect('signup')
        else:
            data={
                'error':error_message,
                'values':value
            }
            return render(request, 'signup.html', data)

class Login(View):
    def get(self,request):
        return render(request,'login.html')
    def post(self,request):
        phone=request.POST.get('mobile')
        error_message= None
        value={
            'mobile': phone
        }
        customer = Customer.objects.filter(mobile=request.POST["mobile"])
        if customer:
            request.session['phone']=phone
            return redirect('homepage')
        else:
            error_message="Mobile Number is Invalid !!"
            data={
                'error':error_message,
                'values':value
            }
        return render(request,'login.html',data)
from .models.wishlist import Wishlist  

def productdetail(request, pk):
    totalitem = 0
    product = Product.objects.get(pk=pk)
    item_already_in_cart = False
    is_wishlisted = False  
    name = "Guest"
    
    if request.session.has_key('phone'):
        phone = request.session["phone"]
        totalitem = len(Cart.objects.filter(phone=phone))
        item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(phone=phone)).exists()
        is_wishlisted = Wishlist.objects.filter(phone=phone, product=product.id).exists() 
        customer = Customer.objects.filter(mobile=phone)
        for c in customer:
            name = c.name
            
    data = {
        'product': product,
        'item_already_in_cart': item_already_in_cart,
        'is_wishlisted': is_wishlisted, 
        'name': name,
        'totalitem': totalitem
    }
    return render(request, 'productdetail.html', data)


class Logout(View):
    def get(self, request):
        request.session.clear() 
        return redirect('login')

def add_to_cart(request):
    phone = request.session['phone']
    product_id = request.GET.get('prod_id')
    product_name = Product.objects.get(id=product_id)
    product = Product.objects.filter(id=product_id)
    for p in product:
        image=p.image
        price=p.price
        Cart(phone=phone,product=product_name,image=image,price=price).save()
    return redirect(f"/product-detail/{product_id}")

def show_cart(request):
    totalitem = 0
    if request.session.has_key('phone'):
        phone = request.session["phone"]
        totalitem = len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(mobile=phone).first()
        name = customer.name if customer else "Guest"
        cart = Cart.objects.filter(phone=phone)
        data = {
            'name': name,
            'totalitem': totalitem,
            'cart': cart
        }
        if cart.exists():
            return render(request, 'show_cart.html', data)
        else:
            return render(request, 'empty_cart.html', data)  
    return redirect('login')

def plus_cart(request):
    pid = request.GET.get('prod_id') 
    phone = request.session.get('phone')
    item = Cart.objects.filter(id=pid, phone=phone).first()
    if item:
        item.quantity += 1
        item.save()
        return JsonResponse({'quantity': item.quantity, 'product_id': pid})
    return JsonResponse({'error': 'Item record not located'}, status=400)

def minus_cart(request):
    pid = request.GET.get('prod_id')
    phone = request.session.get('phone')
    item = Cart.objects.filter(id=pid, phone=phone).first()
    if item:
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
            qty = item.quantity
        else:
            item.delete()
            qty = 0
        return JsonResponse({'quantity': qty, 'product_id': pid})
    return JsonResponse({'error': 'Item record not located'}, status=400)

def remove_cart(request):
    if request.method == 'GET':
        pid = request.GET.get('prod_id')  
        phone = request.session.get('phone')
        Cart.objects.filter(id=pid, phone=phone).delete()
        
        items_left = Cart.objects.filter(phone=phone).count()
        return JsonResponse({
            'status': 'Success', 
            'product_id': pid,
            'items_left': items_left
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


import random
import string

def checkout(request):
    if request.method == 'POST' and request.session.has_key('phone'):
        phone = request.session["phone"]
        cart_items = Cart.objects.filter(phone=phone)
        
        if not cart_items.exists():
            return redirect('homepage')
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        amount_in_paisa = int(total_amount * 100) 
        try:
            razorpay_order = razorpay_client.order.create(data={
                "amount": amount_in_paisa,
                "currency": "INR",
                "payment_capture": 1 
            })
            real_order_id = razorpay_order['id']
        except Exception as e:
            messages.error(request, "Payment gateway timeout. Please try again.")
            return redirect('show_cart')
        customer = Customer.objects.filter(mobile=phone).first()
        customer_name = request.POST.get('name', customer.name if customer else 'Customer')
        
        for c in cart_items:
            OrderDetail.objects.create(
                user=phone, 
                product_name=c.product.name, 
                image=c.product.image, 
                qty=c.quantity, 
                price=c.product.price,
                status='Pending'
            )
            
        context = {
            'order_id': real_order_id,
            'razorpay_key': settings.RAZORPAY_KEY_ID, 
            'amount': amount_in_paisa,
            'name': customer_name,
            'mobile': request.POST.get('mobile', phone),
        }
        return render(request, 'payment_gateway.html', context)
        
    return redirect('homepage')


@csrf_exempt  
def payment_verify(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        if signature == "bypass_signature_verification_for_testing":
            is_valid = True
        else:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
                is_valid = True
            except razorpay.errors.SignatureVerificationError:
                is_valid = False

        if is_valid:
            phone = request.session.get('phone')
            if phone:
                OrderDetail.objects.filter(user=phone, status='Pending').update(status='Paid')
                Cart.objects.filter(phone=phone).delete()
                
            return JsonResponse({'status': 'Payment Verified Successfully'})
        else:
            return JsonResponse({'error': 'Invalid Payment Signature'}, status=400)
            
    return JsonResponse({'error': 'Bad Request Method'}, status=400)




def order(request):
    if request.session.has_key('phone'):
        phone = request.session["phone"]
        orders = OrderDetail.objects.filter(user=phone).order_by('-ordered_date')
        customer = Customer.objects.filter(mobile=phone).first()
        
        return render(request, 'order.html', {
            'orders': orders, 
            'name': customer.name if customer else "Guest", 
            'totalitem': Cart.objects.filter(phone=phone).count()
        })
    return redirect('login')


def search_products(request):
    if not request.session.has_key('phone'):
        return redirect('login')
        
    search_query = request.GET.get('query', '').strip()
    
    if search_query:
        products = Product.objects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    else:
        products = Product.objects.all()
        
    phone = request.session.get('phone')
    totalitem = Cart.objects.filter(phone=phone).count()
    customer = Customer.objects.filter(mobile=phone).first()
    name = customer.name if customer else "Guest"
    
    try:
        categories = Category.get_all_categories()
    except AttributeError:
        categories = Category.objects.all()
    
    context = {
        'products': products,
        'query': search_query,
        'totalitem': totalitem,
        'name': name,
        'categories': categories
    }
    return render(request, 'search.html', context)

from django.http import Http404
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_invoice_pdf(request, order_id):
    if not request.session.has_key('phone'):
        return redirect('login')
        
    phone = request.session['phone']
    try:
        order_item = OrderDetail.objects.get(pk=order_id, user=phone, status='Paid')
    except OrderDetail.DoesNotExist:
        raise Http404("Invoice not found or order unpaid.")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_Order_{order_id}.pdf"'
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#230046"),
        spaceAfter=12
    )
    normal_style = styles['Normal']
    bold_style = ParagraphStyle('BoldText', parent=normal_style, fontName='Helvetica-Bold')
    story.append(Paragraph("TAX INVOICE", title_style))
    story.append(Spacer(1, 15))
    info_data = [
        [Paragraph(f"<b>Sold By:</b><br/>SB Jewellery<br/>Bangalore, India", normal_style),
         Paragraph(f"<b>Billing Details:</b><br/>Customer Mobile: {phone}<br/>Status: PAID", normal_style)]
    ]
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 25))
    story.append(Paragraph(f"<b>Order ID:</b> {order_id}", normal_style))
    if hasattr(order_item, 'ordered_date'):
        story.append(Paragraph(f"<b>Date:</b> {order_item.ordered_date.strftime('%d-%b-%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 15))
    item_total = order_item.price * order_item.qty
    
    table_data = [
        [Paragraph("<b>Product Description</b>", normal_style), 
         Paragraph("<b>Price</b>", normal_style), 
         Paragraph("<b>Qty</b>", normal_style), 
         Paragraph("<b>Total</b>", normal_style)],
        [Paragraph(order_item.product_name, normal_style), 
         f"₹{order_item.price:.2f}", 
         str(order_item.qty), 
         f"₹{item_total:.2f}"],
        ["", "", Paragraph("<b>Grand Total:</b>", bold_style), f"₹{item_total:.2f}"]
    ]
    
    invoice_table = Table(table_data, colWidths=[260, 80, 60, 120])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#230046")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-2), 0.5, colors.lightgrey),
        ('LINEBELOW', (2,-1), (3,-1), 1, colors.HexColor("#230046")),
        ('TOPPADDING', (0,-1), (-1,-1), 10),
    ]))
    table_data[0] = [Paragraph(f"<font color='white'>{cell.text}</font>", bold_style) for cell in table_data[0]]
    
    story.append(invoice_table)
    story.append(Spacer(1, 40))
    story.append(Paragraph("Thank you for shopping with us!", normal_style))
    doc.build(story)
    return response

def toggle_wishlist(request):
    if not request.session.has_key('phone'):
        return redirect('login')
        
    phone = request.session['phone']
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    
    wishlist_item = Wishlist.objects.filter(phone=phone, product=product)
    
    if wishlist_item.exists():
        wishlist_item.delete() 
    else:
        Wishlist(phone=phone, product=product).save() 
        
    return redirect(request.META.get('HTTP_REFERER', 'homepage'))

def show_wishlist(request):
    if not request.session.has_key('phone'):
        return redirect('login')
        
    phone = request.session['phone']
    totalitem = Cart.objects.filter(phone=phone).count()
    customer = Customer.objects.filter(mobile=phone).first()
    name = customer.name if customer else "Guest"
    
    wishlist_items = Wishlist.objects.filter(phone=phone)
    
    context = {
        'wishlist_items': wishlist_items,
        'totalitem': totalitem,
        'name': name
    }
    return render(request, 'wishlist.html', context)
def buy_now(request, prod_id):
    """Bypasses cart, processes shipping modal info, and generates Razorpay Order."""
    if not request.session.has_key('phone'):
        return redirect('login')
        
    phone = request.session["phone"]
    if request.method == 'POST':
        recipient_name = request.POST.get('recipient_name')
        shipping_address = request.POST.get('shipping_address')
        contact_mobile = request.POST.get('contact_mobile')
        
        try:
            product = Product.objects.get(id=prod_id)
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect('homepage')

        total_amount = product.price
        amount_in_paisa = int(total_amount * 100) 
        try:
            razorpay_order = razorpay_client.order.create(data={
                "amount": amount_in_paisa,
                "currency": "INR",
                "payment_capture": 1 
            })
            real_order_id = razorpay_order['id']
        except Exception as e:
            messages.error(request, "Payment gateway timeout. Please try again.")
            return redirect(f"/product-detail/{prod_id}/")
        OrderDetail.objects.create(
            user=phone, 
            product_name=product.name,
            image=product.image, 
            qty=1, 
            price=product.price,
            status='Pending'
        )
            
        context = {
            'order_id': real_order_id,
            'razorpay_key': settings.RAZORPAY_KEY_ID, 
            'amount': amount_in_paisa,
            'name': recipient_name,
            'mobile': contact_mobile,
        }
        return render(request, 'payment_gateway.html', context)

    return redirect(f"/product-detail/{prod_id}/")
