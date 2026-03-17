from django.db import models

# Create your models here.
# models.py
from django.db import models

class CafeHubDatabase(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20)
    user_phone = models.CharField(max_length=15)
    user_city = models.CharField(max_length=100)
    user_register_date = models.DateTimeField()
    cafe_id = models.IntegerField()
    cafe_name = models.CharField(max_length=200)
    cafe_city = models.CharField(max_length=100)
    cafe_state = models.CharField(max_length=100)
    cafe_address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    cafe_rating = models.FloatField()
    total_reviews = models.IntegerField()
    open_status = models.CharField(max_length=10)
    opening_time = models.CharField(max_length=10)
    closing_time = models.CharField(max_length=10)
    vendor_id = models.IntegerField()
    vendor_name = models.CharField(max_length=200)
    vendor_email = models.EmailField()
    vendor_phone = models.CharField(max_length=15)
    partner_cafe = models.CharField(max_length=5)
    menu_item_id = models.IntegerField()
    menu_item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    price = models.CharField(max_length=20)  # ₹269 format
    available = models.CharField(max_length=5)
    order_id = models.IntegerField()
    order_date = models.DateTimeField()
    order_status = models.CharField(max_length=50)
    quantity = models.IntegerField()
    total_amount = models.IntegerField()
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=20)
    coupon_code = models.CharField(max_length=50, null=True, blank=True)
    discount_percent = models.IntegerField(null=True, blank=True)
    coupon_valid_till = models.DateTimeField(null=True, blank=True)
    review_id = models.IntegerField(null=True, blank=True)
    review_rating = models.IntegerField(null=True, blank=True)
    review_comment = models.TextField(null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    wishlist_status = models.CharField(max_length=5, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    account_status = models.CharField(max_length=20)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField()

    class Meta:
        db_table = 'chh_database'  # This matches your actual table name

    def __str__(self):
        return f"{self.username} - {self.cafe_name}"

#django superuser
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Vendor Model
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile', null=True, blank=True)
    vendor_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    cafe_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=100, choices=[
        ('cafe', 'Cafe'),
        ('coffee_shop', 'Coffee Shop'),
        ('restaurant', 'Restaurant with Cafe'),
        ('bakery', 'Bakery with Cafe'),
        ('other', 'Other'),
    ])
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    years_in_business = models.IntegerField(default=0)
    opening_time = models.TimeField(default='08:00')
    closing_time = models.TimeField(default='22:00')
    description = models.TextField(blank=True, null=True)
    seating_capacity = models.IntegerField(default=0)
    amenities = models.JSONField(default=list, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    profile_photo = models.ImageField(upload_to='vendors/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cafe_name

    class Meta:
        ordering = ['-created_at']

# Cafe Model
class Cafe(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='cafes', null=True, blank=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()
    rating = models.FloatField(default=0.0)
    address = models.TextField()
    description = models.TextField(blank=True, null=True)
    is_partner = models.BooleanField(default=False)
    cafe_type = models.CharField(max_length=50, default='vendor')
    opening_hours = models.CharField(max_length=100, blank=True, null=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    contact = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    images = models.JSONField(default=list, blank=True)
    amenities = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-rating']

# Coupon Model
class Coupon(models.Model):
    COUPON_STATUS = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('redeemed', 'Redeemed'),
    ]
    
    COUPON_TYPE = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='coupons', null=True, blank=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPE, default='percentage')
    discount_value = models.IntegerField(default=10, help_text="Discount percentage or fixed amount")
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    usage_limit = models.IntegerField(null=True, blank=True, help_text="Maximum number of times coupon can be used")
    times_used = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=COUPON_STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.discount_value}%"

    class Meta:
        ordering = ['-created_at']

# Transaction Model
class Transaction(models.Model):
    PAYMENT_METHODS = [
        ('razorpay', 'Razorpay'),
        ('cod', 'Cash on Delivery'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    transaction_id = models.CharField(max_length=100, unique=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vendor_share = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='razorpay')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_id} - ₹{self.transaction_amount}"

    class Meta:
        ordering = ['-date']

# Order Model
class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    items = models.JSONField(default=list)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Transaction.PAYMENT_METHODS)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    applied_coupon = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    delivery_address = models.JSONField(default=dict)
    estimated_delivery = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_id}"

    class Meta:
        ordering = ['-created_at']

# Product Review Model
class ProductReview(models.Model):
    product_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    date = models.DateField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Review for Product {self.product_id} by {self.user.username}"

# Favorite Cafe Model
class FavoriteCafe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_cafes')
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'cafe']
    
    def __str__(self):
        return f"{self.user.username} - {self.cafe.name}"

# User Activity Log
class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('purchase', 'Purchase'),
        ('coupon_used', 'Coupon Used'),
        ('review', 'Review'),
        ('favorite', 'Favorite'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']

