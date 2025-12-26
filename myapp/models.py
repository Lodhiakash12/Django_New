from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=100)
    mobile=models.PositiveBigIntegerField()
    profile_picture=models.ImageField(upload_to="profile_picture/")
    address=models.TextField()
    email=models.EmailField()
    password=models.CharField(max_length=100)
    usertype=models.CharField(max_length=100,default="buyer")
     

    def __str__(self):
        return self.fname+""+self.lname
    
class Product(models.Model):
    category=(
        ("Chair","Chair"),
        ("Sofa","Sofa"),
        ("Bed","Bed"),
        ("Table","Table"),
    )
    seller=models.ForeignKey(User,on_delete=models.CASCADE)
    product_category=models.CharField(max_length=100,choices=category)
    product_name=models.CharField(max_length=100)
    product_price=models.PositiveIntegerField()
    product_desc=models.TextField()
    product_image=models.ImageField(upload_to="product_images/")

    def __str__(self):
        return self.seller.fname+"-"+self.product_name
    
class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    time=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.fname+"-"+self.product.product_name
     

class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)     
    time=models.DateTimeField(default=timezone.now)
    product_price=models.PositiveIntegerField()
    product_qty=models.PositiveIntegerField()
    total_price=models.PositiveIntegerField()
    payment_status=models.BooleanField(default=False)

    def __str__(self):
        return self.user.fname+" - "+self.product.product_name
    
class Contact(models.Model):
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    
    
    def __str__(self):
        return self.fname+""+self.lname
