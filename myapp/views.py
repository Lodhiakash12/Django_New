from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart,Contact
from django.core.mail import send_mail
from django.conf import settings
import random
import requests
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import stripe
from django.contrib import messages


YOUR_DOMAIN = 'http://localhost:8000'
stripe.api_key = settings.STRIPE_PRIVATE_KEY

# Create your views here.
def index(request):
    try:
        user = User.objects.get(email=request.session['email'])
        if user.usertype == "buyer":
            return render(request, 'index.html')
        else:
            return render(request, 'seller-index.html')
    except:
        return render(request, 'index.html')

def shop(request):
    products=Product.objects.all()
    return render(request,'shop.html',{'products':products})

def chair(request):
    products=Product.objects.filter(product_category="Chair")
    return render(request,'shop.html',{'products':products})
def sofa(request):
    products=Product.objects.filter(product_category="Sofa")
    return render(request,'shop.html',{'products':products})
def bed(request):
    products=Product.objects.filter(product_category="Bed")
    return render(request,'shop.html',{'products':products})
def table(request):
    products=Product.objects.filter(product_category="Table")
    return render(request,'shop.html',{'products':products})

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def blog(request):
    return render(request, 'blog.html')

def contact(request):
    if request.method == "POST":
        Contact.objects.create(
            fname=request.POST['fname'],
            lname=request.POST['lname'],
            email=request.POST['email'],
            message=request.POST['message'],
        )
        msg = "Contact message sent successfully"
        return render(request, 'contact.html', {'msg': msg})
    
    try:
        user = User.objects.get(email=request.session['email'])
        if user.usertype == "buyer":
            return render(request, 'contact.html')
        else:
            
            contacts = Contact.objects.all().order_by('id')
            return render(request, 'seller-contact.html', {'contacts': contacts})
    except:
        return render(request, 'contact.html')
 
def signup(request):
    if request.method == "POST":
        try:
            User.objects.get(email=request.POST['email'])
            msg = "Email Already Registered"
            return render(request, 'login.html', {'msg': msg})
        except:
            if request.POST['password'] == request.POST['cpassword']:
                User.objects.create(
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    address=request.POST['address'],
                    password=request.POST['password'],
                    profile_picture=request.FILES['profile_picture'],
                    usertype=request.POST.get('usertype', 'buyer')  # Fixed: Added usertype field
                )
                msg = "User sign up successfully"
                return render(request, 'login.html', {'msg': msg})
            else:
                msg = "Password & confirm password does not match"
                return render(request, 'signup.html', {'msg': msg})
    else:
        return render(request, 'signup.html') 

def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            if user.password == request.POST['password']:
                request.session['email'] = user.email
                request.session['fname'] = user.fname
                request.session['lname'] = user.lname
                request.session['profile_picture'] = user.profile_picture.url
                
                if user.usertype == "buyer":
                    return render(request, 'index.html')
                else:
                    return render(request, 'seller-index.html')
            else:
                msg = "Incorrect password" 
                return render(request, 'login.html', {'msg': msg}) 
        except:
            msg = "Email Not Registered" 
            return render(request, 'login.html', {'msg': msg})      
    else:
        return render(request, 'login.html')  

def logout(request):
    try:
        del request.session['email']       
        del request.session['fname']  
        del request.session['lname']   
        del request.session['profile_picture'] 
    except:
        pass
    msg = "Logged out successfully"
    return render(request, 'login.html', {'msg': msg})

def profile(request):
    # Fixed: Check if user is logged in
    if 'email' not in request.session:
        return redirect('login')
    
    user = User.objects.get(email=request.session['email'])
    if request.method == 'POST':
        user.fname = request.POST['fname']
        user.lname = request.POST['lname']
        user.mobile = request.POST['mobile']
        user.address = request.POST['address']
        try:
            user.profile_picture = request.FILES['profile_picture']
        except:
            pass
        user.save() 
        request.session['fname'] = user.fname   
        request.session['profile_picture'] = user.profile_picture.url
        msg = "Profile updated successfully" 
        if user.usertype == "buyer":
            return render(request, 'profile.html', {'user': user, 'msg': msg}) 
        else:
            return render(request, 'seller-profile.html', {'user': user, 'msg': msg})    
    else:
        if user.usertype == "buyer":
            return render(request, 'profile.html', {'user': user}) 
        else:
            return render(request, 'seller-profile.html', {'user': user})

def change_password(request):
  
    if 'email' not in request.session:
        return redirect('login')
    
    user = User.objects.get(email=request.session['email'])
    if request.method == 'POST':
        if user.password == request.POST['old_password']:
            if request.POST['new_password'] == request.POST['cnew_password']:
                if user.password != request.POST['new_password']:
                    user.password = request.POST['new_password']
                    user.save()
                    try:
                        del request.session['email']       
                        del request.session['fname']    
                        del request.session['profile_picture']
                    except:
                        pass
                    msg = "Password changed successfully"
                    return render(request, 'login.html', {'msg': msg})  
                else:
                    msg = "Your new password can't be the same as your old password"
                    if user.usertype == "buyer":
                        return render(request, 'change-password.html', {'msg': msg})
                    else:
                        return render(request, 'seller-change-password.html', {'msg': msg})
            else:
                msg = "New password & confirm new password does not match" 
                if user.usertype == "buyer":
                    return render(request, 'change-password.html', {'msg': msg})
                else:
                    return render(request, 'seller-change-password.html', {'msg': msg}) 
        else:
            msg = "Old password does not match"
            if user.usertype == "buyer":
                return render(request, 'change-password.html', {'msg': msg})
            else:
                return render(request, 'seller-change-password.html', {'msg': msg})                     
    else:
        if user.usertype == "buyer":
            return render(request, 'change-password.html')
        else:
            return render(request, 'seller-change-password.html')

def forgot_password(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            otp = random.randint(1000, 9999)
            context = {}
            address = request.POST.get('email')
            subject = "OTP For Forgot Password"
            message = "Your OTP for forgot password is " + str(otp)

            if address and subject and message:
                try:
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [address])
                    context['result'] = 'Email sent successfully'
                    request.session['email1'] = request.POST['email']
                    request.session['otp'] = otp
                except Exception as e:
                    context['result'] = f'Error sending email: {e}'
            else:
                context['result'] = 'All fields are required'
    
            return render(request, "otp.html", context)
        except Exception as e:
            msg = 'Email Not Registered' 
            return render(request, 'forgot-password.html', {'msg': msg})    
    else:   
        return render(request, 'forgot-password.html')

def verify_otp(request):
    # Fixed: Check if OTP exists in session
    if 'otp' not in request.session:
        return render(request, 'forgot-password.html', {'msg': 'Session expired. Please try again.'})
    
    otp1 = int(request.session['otp'])
    otp2 = int(request.POST['otp'])

    if otp1 == otp2:
        del request.session['otp']
        return render(request, 'new-password.html', {'msg': 'Please Set Your New Password'})
    else:
        return render(request, 'otp.html', {'msg': 'Invalid OTP'})

def new_password(request):
    # Fixed: Check if email1 exists in session
    if 'email1' not in request.session:
        return render(request, 'forgot-password.html', {'msg': 'Session expired. Please try again.'})
    
    if request.POST['new_password'] == request.POST['cnew_password']:
        user = User.objects.get(email=request.session['email1'])
        user.password = request.POST['new_password']
        user.save()
        msg = "Password updated successfully"
        del request.session['email1']
        return render(request, 'login.html', {'msg': msg})
    else:
        msg = "New Password & confirm new password does not match"
        return render(request, 'new-password.html', {'msg': msg})

def add_product(request):
    # Fixed: Check if user is logged in
    if 'email' not in request.session:
        return redirect('login')
    
    seller = User.objects.get(email=request.session['email'])
    
    # Fixed: Check if user is actually a seller
    if seller.usertype != 'seller':
        msg = "Only sellers can add products"
        return render(request, 'index.html', {'msg': msg})
    
    if request.method == "POST":
        try:
            Product.objects.create(
                seller=seller,
                product_category=request.POST['product_category'],
                product_name=request.POST['product_name'],
                product_price=request.POST['product_price'],
                product_desc=request.POST['product_desc'],
                product_image=request.FILES['product_image'],
            )
            msg = "Product Added Successfully"
            return render(request, 'add-product.html', {'msg': msg})
        except Exception as e:
            msg = f"Error adding product: {str(e)}"
            return render(request, 'add-product.html', {'msg': msg})
    else:
        return render(request, 'add-product.html')
    
def view_product(request):
    seller=User.objects.get(email=request.session['email'])
    products=Product.objects.filter(seller=seller)
    return render(request,'view-product.html',{'products':products})

def seller_product_details(request,pk):
    product=Product.objects.get(pk=pk)
    return render(request,'seller-product-details.html',{'product':product})

def seller_product_edit(request,pk):
    product=Product.objects.get(pk=pk)
    if request.method=='POST':
        product.product_category=request.POST['product_category']
        product.product_name=request.POST['product_name']
        product.product_desc=request.POST['product_desc']
        product.product_price=request.POST['product_price']
        try:
            product.product_image=request.FILES['product_image']
        except:
            pass
        
        product.save() 
         
        return redirect('view-product')
    else:
        return render(request,'seller-product-edit.html',{'product':product})
    
def seller_product_delete(request,pk):
    product=Product.objects.get(pk=pk)
    product.delete()
    return redirect('view-product')

def product_details(request,pk):
    if 'email' not in request.session:
        messages.warning(request, 'You need to login to view product details.')
        return redirect('login')
    wishlist_flag=False
    cart_flag=False
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    try:
        Wishlist.objects.get(user=user,product=product)
        wishlist_flag=True
    except:
        pass
    try:
        Cart.objects.get(user=user,product=product,payment_status=False)
        cart_flag=True
    except:
        pass
    return render(request,'product-details.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})
def add_to_wishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Wishlist.objects.create(user=user,product=product)
    return redirect("wishlist")

def wishlist(request):
    user=User.objects.get(email=request.session['email'])
    wishlists=Wishlist.objects.filter(user=user)
    request.session['wishlist_count']=len(wishlists)
    return render(request,'wishlist.html',{'wishlists':wishlists})
 

def remove_from_wishlist(request,pk):
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    wishlist=Wishlist.objects.get(user=user,product=product)
    wishlist.delete()
    return redirect('wishlist')

def add_to_cart(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Cart.objects.create(
        user=user,
        product=product,
        product_price=product.product_price,
        product_qty=1,
        total_price=product.product_price,
        payment_status=False
        )
    return redirect('cart')

def cart(request):
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            return redirect('login')
        
        user = User.objects.get(email=request.session['email'])
        carts = Cart.objects.filter(user=user, payment_status=False)
        
        
        
        
        net_price = 0
        for cart_item in carts:
            # Ensure total_price is calculated
            if not cart_item.total_price:
                cart_item.total_price = cart_item.product.product_price * cart_item.product_qty
                cart_item.save()
            net_price += cart_item.total_price
        
        # Update cart count in session
        request.session['cart_count'] = len(carts)
        
        return render(request, 'cart.html', {
            'carts': carts,
            'net_price': net_price
        })
    
    except User.DoesNotExist:
        return redirect('login')
    except Exception as e:
        print(f"Cart error: {e}")
        return redirect('shop')
 

def remove_from_cart(request, pk):
    user = User.objects.get(email=request.session['email'])
    product = Product.objects.get(pk=pk)
    
    # Option 1: Remove the first matching item
    cart = Cart.objects.filter(user=user, product=product).first()
    if cart:
        cart.delete()
    
    # Option 2: Remove ALL duplicate items (recommended)
    # Cart.objects.filter(user=user, product=product).delete()
    
    return redirect('cart')
    

def change_qty(request):
    cart=Cart.objects.get(pk=int(request.POST['cid']))
    product_qty=int(request.POST['product_qty'])
    cart.total_price=cart.product_price*product_qty
    cart.product_qty=product_qty
    cart.save()

    return redirect('cart')

@csrf_exempt
def create_checkout_session(request):
	amount = int(json.load(request)['post_data'])
	final_amount=amount*100
	user=User.objects.get(email=request.session['email'])
	user_name=f"{user.fname} {user.lname}"
	user_address=f"{user.address}"
	user_mobile=f"{user.mobile}"
	session = stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
			'price_data': {
				'currency': 'inr',
				'unit_amount': final_amount,
				'product_data': {
					'name': 'Checkout Session Data',
					'description':f'''Customer:{user_name},\n\n
					Address:{user_address},\n
					Mobile:{user_mobile}''',
				},
			},
			'quantity': 1,
			}],
		mode='payment',
		success_url=YOUR_DOMAIN + '/success.html',
		cancel_url=YOUR_DOMAIN + '/cancel.html',
		customer_email=user.email,
		shipping_address_collection={
			'allowed_countries':['IN'],
		}
		)
	return JsonResponse({'id': session.id})

from django.shortcuts import redirect

def success(request):
    email = request.session.get('email')

    if not email:
        return redirect('login')   # prevent crash

    user = User.objects.get(email=email)

    carts = Cart.objects.filter(user=user, payment_status=False)
    for i in carts:
        i.payment_status = True
        i.save()

    carts = Cart.objects.filter(user=user, payment_status=False)
    request.session['cart_count'] = carts.count()

    return render(request, 'success.html')


def cancel(request):
	return render(request,'cancel.html')

def myorder(request):
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status=True)
    return render(request,'myorder.html',{'carts':carts})