import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from shopping.models import (
    UserProfile, Category, Brand, Product, ProductSpec, Seller,
    SellerOffer, PriceHistory, Review, Wishlist, WishlistItem, Cart, CartItem, Order, OrderItem
)

class Command(BaseCommand):
    help = "Seeds the database with realistic AI Shopping Agent products, sellers, reviews, and price histories."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting database seeding process..."))

        # Create Demo User & Profile
        user, _ = User.objects.get_or_create(username='demo_shopper', defaults={'first_name': 'Jayesh', 'email': 'jayesh@example.com'})
        user.set_password('demo1234')
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.favorite_brands = ['Asus', 'Apple', 'Sony', 'Dell']
        profile.preferred_categories = ['Electronics', 'Furniture', 'Fashion']
        profile.shopping_personality = "Tech Advisor: Prioritize performance and reliability over brand"
        profile.saved_money_total = 31400.00
        profile.save()

        # Categories
        cat_electronics, _ = Category.objects.get_or_create(name='Electronics', slug='electronics', icon='fa-laptop')
        cat_fashion, _ = Category.objects.get_or_create(name='Fashion', slug='fashion', icon='fa-shirt')
        cat_furniture, _ = Category.objects.get_or_create(name='Furniture', slug='furniture', icon='fa-chair')
        cat_gift, _ = Category.objects.get_or_create(name='Gifts & Accessories', slug='gifts', icon='fa-gift')

        # Brands
        brand_asus, _ = Brand.objects.get_or_create(name='ASUS', slug='asus', sustainability_rating=85)
        brand_dell, _ = Brand.objects.get_or_create(name='Dell', slug='dell', sustainability_rating=82)
        brand_apple, _ = Brand.objects.get_or_create(name='Apple', slug='apple', sustainability_rating=90)
        brand_sony, _ = Brand.objects.get_or_create(name='Sony', slug='sony', sustainability_rating=88)
        brand_nike, _ = Brand.objects.get_or_create(name='Nike', slug='nike', sustainability_rating=78)
        brand_logitech, _ = Brand.objects.get_or_create(name='Logitech', slug='logitech', sustainability_rating=84)
        brand_secretlab, _ = Brand.objects.get_or_create(name='Secretlab', slug='secretlab', sustainability_rating=80)

        # Sellers
        seller_a, _ = Seller.objects.get_or_create(name='Marketplace Prime', rating=4.8, return_policy='14-day hassle-free returns', delivery_reliability_pct=98)
        seller_b, _ = Seller.objects.get_or_create(name='ElectroDirect', rating=4.6, return_policy='7-day replacement', delivery_reliability_pct=94)
        seller_c, _ = Seller.objects.get_or_create(name='TechHub Store', rating=4.5, return_policy='10-day store return', delivery_reliability_pct=92)

        # Product Datasets
        products_data = [
            {
                'title': 'ASUS ROG Zephyrus G16 Gaming Laptop',
                'slug': 'asus-rog-zephyrus-g16',
                'category': cat_electronics,
                'brand': brand_asus,
                'description': 'High-performance ultra-slim gaming laptop with Intel Core i7 13th Gen, NVIDIA RTX 4060 GPU, 16GB DDR5 RAM, 1TB SSD, and 16" 165Hz QHD OLED display. Perfect for coding, gaming, and 4K video editing.',
                'base_price': 78999.00,
                'image_url': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&auto=format&fit=crop&q=80',
                'rating': 4.8,
                'review_count': 142,
                'compatibility_tags': ['usb-c', 'thunderbolt', 'hdmi', 'windows'],
                'usage_tags': ['Programming', 'Gaming', 'Content Creation'],
                'specs': [
                    ('Processor', 'Intel Core i7-13700H', True),
                    ('GPU', 'NVIDIA GeForce RTX 4060 8GB', True),
                    ('RAM', '16GB DDR5 4800MHz', True),
                    ('Storage', '1TB NVMe M.2 SSD', True),
                    ('Display', '16.0" QHD OLED 165Hz', True),
                    ('Weight', '1.9 kg (Ultra Lightweight)', False),
                    ('Battery', '90Wh (Up to 9 hours)', False)
                ]
            },
            {
                'title': 'Dell XPS 15 Developer Edition',
                'slug': 'dell-xps-15-developer',
                'category': cat_electronics,
                'brand': brand_dell,
                'description': 'Premium CNC aluminum developer laptop featuring 13th Gen Intel i7, 32GB RAM, 1TB SSD, and 3.5K OLED Touch screen. Optimized for software engineers and creators.',
                'base_price': 114999.00,
                'image_url': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&auto=format&fit=crop&q=80',
                'rating': 4.7,
                'review_count': 98,
                'compatibility_tags': ['usb-c', 'thunderbolt', 'linux', 'windows'],
                'usage_tags': ['Programming', 'Content Creation', 'Daily Use'],
                'specs': [
                    ('Processor', 'Intel Core i7-13700H', True),
                    ('GPU', 'Intel Iris Xe / RTX 4050', True),
                    ('RAM', '32GB DDR5', True),
                    ('Storage', '1TB PCIe SSD', True),
                    ('Display', '15.6" 3.5K OLED Touch', True)
                ]
            },
            {
                'title': 'Apple MacBook Air M3 (15-inch)',
                'slug': 'apple-macbook-air-m3',
                'category': cat_electronics,
                'brand': brand_apple,
                'description': 'Incredibly thin and fast MacBook powered by Apple M3 chip. 18-hour battery life, 16GB unified memory, silent fanless design.',
                'base_price': 124900.00,
                'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80',
                'rating': 4.9,
                'review_count': 320,
                'compatibility_tags': ['usb-c', 'thunderbolt', 'macos'],
                'usage_tags': ['Programming', 'Daily Use', 'Content Creation'],
                'specs': [
                    ('Processor', 'Apple M3 8-core CPU', True),
                    ('GPU', '10-core GPU', True),
                    ('RAM', '16GB Unified Memory', True),
                    ('Storage', '512GB SSD', True),
                    ('Battery', 'Up to 18 Hours', True)
                ]
            },
            {
                'title': 'Sony WH-1000XM5 Wireless Headphones',
                'slug': 'sony-wh-1000xm5',
                'category': cat_electronics,
                'brand': brand_sony,
                'description': 'Industry-leading noise canceling wireless headphones with Auto NC Optimizer, crystal clear hands-free calling, and 30-hour battery life.',
                'base_price': 29990.00,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80',
                'rating': 4.8,
                'review_count': 450,
                'compatibility_tags': ['bluetooth', '3.5mm'],
                'usage_tags': ['Audio', 'Calls', 'Daily Use'],
                'specs': [
                    ('Noise Cancellation', 'Dual Processor Auto NC', True),
                    ('Battery Life', '30 Hours', True),
                    ('Drivers', '30mm Precision Driver', True)
                ]
            },
            {
                'title': 'Nike ZoomX Vaporfly Running Shoes',
                'slug': 'nike-zoomx-vaporfly',
                'category': cat_fashion,
                'brand': brand_nike,
                'description': 'Lightweight road racing running shoes with full-length carbon fiber plate and responsive ZoomX foam cushioning.',
                'base_price': 3895.00,
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80',
                'rating': 4.6,
                'review_count': 85,
                'compatibility_tags': ['running', 'footwear'],
                'usage_tags': ['Fitness', 'Daily Use'],
                'specs': [
                    ('Material', 'VaporWeave Mesh', True),
                    ('Cushioning', 'ZoomX Foam + Carbon Plate', True),
                    ('Fit', 'Regular Fit', True)
                ]
            },
            {
                'title': 'Logitech MX Master 3S Ergonomic Wireless Mouse',
                'slug': 'logitech-mx-master-3s',
                'category': cat_electronics,
                'brand': brand_logitech,
                'description': 'Performance wireless mouse with 8K DPI tracking on any glass surface, quiet clicks, and electromagnetic scroll wheel.',
                'base_price': 9495.00,
                'image_url': 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&auto=format&fit=crop&q=80',
                'rating': 4.9,
                'review_count': 610,
                'compatibility_tags': ['usb-c', 'bluetooth', 'windows', 'macos'],
                'usage_tags': ['Peripheral', 'Programming', 'WFH'],
                'specs': [
                    ('Sensor', '8000 DPI Darkfield', True),
                    ('Battery', '70 Days full charge', True)
                ]
            },
            {
                'title': 'Secretlab TITAN EVO Ergonomic Gaming Chair',
                'slug': 'secretlab-titan-evo',
                'category': cat_furniture,
                'brand': brand_secretlab,
                'description': 'Premium ergonomic gaming and office chair with 4-way L-ADAPT lumbar support and cold-cure memory foam.',
                'base_price': 42900.00,
                'image_url': 'https://images.unsplash.com/photo-1580481072645-022f9a6d83d0?w=800&auto=format&fit=crop&q=80',
                'rating': 4.7,
                'review_count': 210,
                'compatibility_tags': ['furniture', 'ergonomic'],
                'usage_tags': ['WFH', 'Gaming', 'Furniture'],
                'specs': [
                    ('Lumbar System', '4-Way L-ADAPT', True),
                    ('Material', 'NEO Hybrid Leatherette', True)
                ]
            }
        ]

        for p_data in products_data:
            specs = p_data.pop('specs')
            prod, _ = Product.objects.get_or_create(slug=p_data['slug'], defaults=p_data)

            # Specs
            for skey, sval, is_p in specs:
                ProductSpec.objects.get_or_create(product=prod, spec_key=skey, defaults={'spec_value': sval, 'is_primary': is_p})

            # Offers across 3 sellers
            SellerOffer.objects.get_or_create(product=prod, seller=seller_a, defaults={
                'price': prod.base_price,
                'coupon_discount': 2000.00 if prod.base_price > 20000 else 300.00,
                'bank_offer': 1500.00 if prod.base_price > 20000 else 200.00,
                'delivery_days': 2
            })
            SellerOffer.objects.get_or_create(product=prod, seller=seller_b, defaults={
                'price': prod.base_price * 1.02,
                'coupon_discount': 1000.00,
                'delivery_days': 1
            })

            # Price History (past 30 days)
            now = timezone.now()
            PriceHistory.objects.get_or_create(product=prod, recorded_at=now - timedelta(days=30), defaults={'price': prod.base_price * 1.08})
            PriceHistory.objects.get_or_create(product=prod, recorded_at=now - timedelta(days=15), defaults={'price': prod.base_price * 1.02})
            PriceHistory.objects.get_or_create(product=prod, recorded_at=now - timedelta(days=3), defaults={'price': prod.base_price * 0.95})

            # Sample Reviews
            Review.objects.get_or_create(product=prod, author_name="Rahul V.", defaults={
                'rating': 5,
                'sentiment': 'positive',
                'title': 'Outstanding build quality and fast performance!',
                'comment': f"I purchased the {prod.title} 2 weeks ago. Absolutely delivers on specs!",
                'pros': ['Vibrant display', 'Strong GPU/CPU performance', 'Fast thermal cooling'],
                'cons': ['Average webcam'],
                'is_verified_purchase': True
            })

        self.stdout.write(self.style.SUCCESS("Successfully seeded catalog, sellers, specs, and price histories!"))
