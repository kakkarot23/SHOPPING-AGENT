import json
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    default_budget = models.DecimalField(max_digits=12, decimal_places=2, default=50000.00)
    favorite_brands = models.JSONField(default=list, blank=True)
    preferred_categories = models.JSONField(default=list, blank=True)
    size_clothing = models.CharField(max_length=20, default='L', blank=True)
    size_shoes = models.CharField(max_length=20, default='UK 9', blank=True)
    color_preferences = models.JSONField(default=list, blank=True)
    height_cm = models.IntegerField(default=175, blank=True, null=True)
    weight_kg = models.IntegerField(default=70, blank=True, null=True)
    shopping_personality = models.CharField(
        max_length=100, 
        default="Tech Advisor: Prioritize performance and reliability over brand"
    )
    preference_weights = models.JSONField(default=dict, blank=True)
    saved_money_total = models.DecimalField(max_digits=12, decimal_places=2, default=31400.00)
    total_purchases_count = models.IntegerField(default=12)

    def save(self, *args, **kwargs):
        if not self.preference_weights:
            self.preference_weights = {
                'performance': 25,
                'price': 20,
                'reviews': 20,
                'features': 15,
                'reliability': 10,
                'warranty': 5,
                'delivery': 5
            }
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile for {self.user.username}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='fa-laptop')
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo_icon = models.CharField(max_length=50, default='fa-award')
    sustainability_rating = models.IntegerField(default=80)  # 0 to 100

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.URLField(max_length=500)
    rating = models.FloatField(default=4.5)
    review_count = models.IntegerField(default=120)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    sustainability_score = models.IntegerField(default=82) # 0 to 100
    return_window_days = models.IntegerField(default=14)
    warranty_months = models.IntegerField(default=12)
    compatibility_tags = models.JSONField(default=list, blank=True)
    usage_tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def primary_specs(self):
        return self.specs.filter(is_primary=True)

    @property
    def lowest_offer(self):
        offers = self.offers.filter(stock_status='in_stock')
        if offers.exists():
            return min(offers, key=lambda o: o.effective_price)
        return None


class ProductSpec(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specs')
    spec_key = models.CharField(max_length=100)  # e.g., Processor, RAM, Battery
    spec_value = models.CharField(max_length=255) # e.g., Intel i7 13th Gen, 16GB
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'spec_key')

    def __str__(self):
        return f"{self.product.title} - {self.spec_key}: {self.spec_value}"


class Seller(models.Model):
    name = models.CharField(max_length=100)
    rating = models.FloatField(default=4.7)
    review_count = models.IntegerField(default=1500)
    return_policy = models.CharField(max_length=255, default="14-day hassle-free returns")
    delivery_reliability_pct = models.IntegerField(default=96)

    def __str__(self):
        return self.name


class SellerOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='offers')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    coupon_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    bank_offer = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cashback = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    stock_status = models.CharField(
        max_length=20, 
        choices=[('in_stock', 'In Stock'), ('out_of_stock', 'Out of Stock'), ('pre_order', 'Pre-Order')],
        default='in_stock'
    )
    delivery_days = models.IntegerField(default=2)

    @property
    def effective_price(self):
        return (self.price - self.coupon_discount - self.bank_offer - self.cashback) + self.shipping_fee + self.tax_amount

    def __str__(self):
        return f"{self.product.title} at {self.seller.name} (Effective: ₹{self.effective_price:.2f})"


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_at = models.DateTimeField(default=timezone.now)
    event_label = models.CharField(max_length=100, blank=True, default="Price Check")

    class Meta:
        ordering = ['recorded_at']

    def __str__(self):
        return f"{self.product.title} - ₹{self.price} on {self.recorded_at.strftime('%Y-%m-%d')}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    author_name = models.CharField(max_length=100, default="Shopper")
    rating = models.IntegerField(default=5)
    sentiment = models.CharField(
        max_length=20, 
        choices=[('positive', 'Positive'), ('neutral', 'Neutral'), ('negative', 'Negative')],
        default='positive'
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    pros = models.JSONField(default=list, blank=True)
    cons = models.JSONField(default=list, blank=True)
    is_verified_purchase = models.BooleanField(default=True)
    is_suspicious_fake = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}★ for {self.product.title} by {self.author_name}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    title = models.CharField(max_length=100, default="My Main Wishlist")
    is_collaborative = models.BooleanField(default=False)
    shared_link_token = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_price = models.DecimalField(max_digits=12, decimal_places=2)
    target_alert_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} in {self.wishlist.title}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user or self.session_key}"

    @property
    def total_cost(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller_offer = models.ForeignKey(SellerOffer, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    is_bundle_item = models.BooleanField(default=False)

    @property
    def unit_price(self):
        if self.seller_offer:
            return self.seller_offer.effective_price
        return self.product.base_price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.title}"


class PriceAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    target_price = models.DecimalField(max_digits=12, decimal_places=2)
    alert_type = models.CharField(
        max_length=30,
        choices=[
            ('target_reached', 'Target Price Reached'),
            ('price_drop', 'Price Drop Alert'),
            ('back_in_stock', 'Back in Stock'),
            ('major_discount', 'Festival / Major Discount')
        ],
        default='target_reached'
    )
    is_active = models.BooleanField(default=True)
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert: {self.product.title} <= ₹{self.target_price}"


class AutopilotTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='autopilot_tasks')
    query_prompt = models.TextField()
    max_budget = models.DecimalField(max_digits=12, decimal_places=2)
    duration_days = models.IntegerField(default=30)
    status = models.CharField(
        max_length=30,
        choices=[
            ('monitoring', 'Monitoring Market'),
            ('opportunity_found', 'Deal Opportunity Found'),
            ('completed', 'Completed'),
            ('paused', 'Paused')
        ],
        default='monitoring'
    )
    recommended_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    buy_recommendation = models.CharField(
        max_length=30,
        choices=[('BUY_NOW', 'BUY NOW'), ('WAIT', 'WAIT FOR PRICE DROP'), ('CONSIDER_ALTERNATIVE', 'CONSIDER ALTERNATIVE')],
        default='WAIT'
    )
    last_checked = models.DateTimeField(default=timezone.now)
    log_history = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Autopilot: {self.query_prompt[:40]}... (Status: {self.status})"


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_sessions')
    title = models.CharField(max_length=200, default="Shopping Session")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session: {self.title} ({self.created_at.strftime('%Y-%m-%d')})"


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('ai', 'AI')], default='user')
    message_text = models.TextField()
    extracted_intent = models.JSONField(default=dict, blank=True)
    recommended_products = models.ManyToManyField(Product, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.sender.upper()}] {self.message_text[:40]}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=30,
        choices=[('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('returned', 'Returned')],
        default='processing'
    )
    tracking_code = models.CharField(max_length=100, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order_number} (₹{self.total_amount})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.title} in Order #{self.order.order_number}"
