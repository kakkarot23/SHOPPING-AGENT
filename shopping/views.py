import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from shopping.models import (
    Product, Category, Brand, SellerOffer, Review, Wishlist, WishlistItem,
    Cart, CartItem, PriceAlert, AutopilotTask, ChatSession, ChatMessage, UserProfile, Order
)
from shopping.ai_engines.intent_engine import IntentEngine
from shopping.ai_engines.scoring_engine import ScoringEngine
from shopping.ai_engines.comparison_engine import ComparisonEngine
from shopping.ai_engines.review_intelligence import ReviewIntelligenceEngine
from shopping.ai_engines.price_predictor import PricePredictorEngine
from shopping.ai_engines.budget_bundle_engine import BudgetBundleEngine
from shopping.ai_engines.visual_search_engine import VisualSearchEngine
from shopping.ai_engines.compatibility_engine import CompatibilityEngine
from shopping.ai_engines.autopilot_agent import AutopilotAgent


def _get_or_create_default_user():
    user, _ = User.objects.get_or_create(username='demo_shopper', defaults={'first_name': 'Jayesh', 'email': 'jayesh@example.com'})
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return user, profile


# 1. AI Shopping Command Center (Home Page)
def command_center(request):
    user, profile = _get_or_create_default_user()
    recent_products = Product.objects.all().order_by('-rating')[:6]
    categories = Category.objects.all()

    default_intent = {
        'budget': 80000.0,
        'usage': ['Programming', 'Gaming'],
        'required_features': ['High RAM', 'Dedicated GPU'],
        'brands': ['Asus', 'Dell', 'Lenovo']
    }
    top_recommendations = ScoringEngine.rank_and_badge_products(recent_products, default_intent)[:4]

    context = {
        'profile': profile,
        'categories': categories,
        'top_recommendations': top_recommendations,
        'sample_prompts': [
            "Find me the best laptop under ₹80,000 for programming and gaming.",
            "I need a wedding gift for my sister under ₹5,000.",
            "Find running shoes for daily use under ₹4,000.",
            "I have ₹1 lakh for a phone, watch and earbuds.",
            "Build me a complete WFH setup under ₹1,50,000."
        ]
    }
    return render(request, 'shopping/command_center.html', context)


# 2. Product Catalog & Search
def product_list(request):
    user, profile = _get_or_create_default_user()
    query = request.GET.get('q', '')
    cat_slug = request.GET.get('category', '')
    brand_slug = request.GET.get('brand', '')
    max_price = request.GET.get('max_price', '')

    products = Product.objects.all()

    intent = {'original_query': query, 'budget': float(max_price) if max_price and max_price.isdigit() else None}

    if query:
        extracted = IntentEngine.extract_intent(query)
        intent.update(extracted)
        if extracted.get('category') and extracted['category'] != 'General':
            products = products.filter(category__name__icontains=extracted['category'])
        products = products.filter(title__icontains=query) | products.filter(description__icontains=query)

    if cat_slug:
        products = products.filter(category__slug=cat_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if max_price and max_price.isdigit():
        products = products.filter(base_price__lte=float(max_price))

    scored_products = ScoringEngine.rank_and_badge_products(products, intent, profile.preference_weights)

    context = {
        'scored_products': scored_products,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'query': query,
        'intent': intent,
        'profile': profile
    }
    return render(request, 'shopping/product_list.html', context)


# 3. Product Detail View
def product_detail(request, slug):
    user, profile = _get_or_create_default_user()
    product = get_object_or_404(Product, slug=slug)

    review_insights = ReviewIntelligenceEngine.analyze_reviews(product)
    price_prediction = PricePredictorEngine.predict_buy_opportunity(product)
    seller_offers = product.offers.all().order_by('price')

    # Calculate effective price for lowest seller offer
    best_offer = seller_offers.first()

    # Alternatives
    alternatives = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]
    alt_scored = ScoringEngine.rank_and_badge_products(alternatives, {})

    # Compatibility check with user cart
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_items = [ci.product for ci in cart.items.all()]
    cart_items.append(product)
    compatibility = CompatibilityEngine.check_compatibility(cart_items)

    context = {
        'product': product,
        'best_offer': best_offer,
        'seller_offers': seller_offers,
        'review_insights': review_insights,
        'price_prediction': price_prediction,
        'alternatives': alt_scored,
        'compatibility': compatibility,
        'price_history_json': json.dumps([
            {'date': h.recorded_at.strftime('%b %d'), 'price': float(h.price)}
            for h in product.price_history.all()
        ])
    }
    return render(request, 'shopping/product_detail.html', context)


# 4. Product Comparison View
def compare(request):
    user, profile = _get_or_create_default_user()
    product_ids = request.GET.getlist('id')

    if not product_ids:
        # Default compare first 3 products
        products = list(Product.objects.all()[:3])
    else:
        products = list(Product.objects.filter(id__in=product_ids))

    comparison_data = ComparisonEngine.compare_products(products, user_budget=float(profile.default_budget))

    context = {
        'products': products,
        'all_products': Product.objects.all(),
        'spec_keys': comparison_data.get('spec_keys', []),
        'grid': comparison_data.get('grid', []),
        'verdict': comparison_data.get('verdict', ''),
        'cheapest_product': comparison_data.get('cheapest_product'),
        'highest_rated_product': comparison_data.get('highest_rated_product')
    }
    return render(request, 'shopping/compare.html', context)


# 5. AI Gift Finder Wizard
def gift_finder(request):
    user, profile = _get_or_create_default_user()
    results = None
    if request.method == 'POST':
        who = request.POST.get('who', 'Sister')
        age = request.POST.get('age', '25')
        occasion = request.POST.get('occasion', 'Birthday')
        budget = float(request.POST.get('budget', 5000))
        interests = request.POST.get('interests', 'Fashion + Tech')

        gift_query = f"Gift for {who} age {age} for {occasion} under ₹{budget} interested in {interests}"
        intent = IntentEngine.extract_intent(gift_query)

        products = Product.objects.filter(base_price__lte=budget)
        if not products.exists():
            products = Product.objects.all()

        results = ScoringEngine.rank_and_badge_products(products, intent)[:4]

    return render(request, 'shopping/gift_finder.html', {'results': results})


# 6. Smart Bundle Builder & Budget Optimizer
def bundle_builder(request):
    user, profile = _get_or_create_default_user()
    bundle_data = None
    total_budget = 100000.0
    setup_type = 'wfh'

    if request.method == 'POST' or request.GET.get('budget'):
        total_budget = float(request.POST.get('budget') or request.GET.get('budget') or 100000)
        setup_type = request.POST.get('setup_type') or request.GET.get('setup_type') or 'wfh'
        bundle_data = BudgetBundleEngine.build_smart_bundle(total_budget, setup_type)

    if not bundle_data:
        bundle_data = BudgetBundleEngine.build_smart_bundle(100000.0, 'wfh')

    context = {
        'bundle_data': bundle_data,
        'total_budget': total_budget,
        'setup_type': setup_type
    }
    return render(request, 'shopping/bundle_builder.html', context)


# 7. AI Shopping Autopilot Dashboard
def autopilot(request):
    user, profile = _get_or_create_default_user()
    if request.method == 'POST':
        prompt = request.POST.get('query_prompt')
        budget = request.POST.get('max_budget')
        if prompt:
            AutopilotAgent.create_autopilot_task(
                user=user,
                query_text=prompt,
                max_budget=float(budget) if budget else None
            )
            return redirect('autopilot')

    tasks = AutopilotTask.objects.filter(user=user).order_by('-created_at')
    return render(request, 'shopping/autopilot.html', {'tasks': tasks})


# 8. Personal Shopping Analytics
def analytics(request):
    user, profile = _get_or_create_default_user()
    orders = Order.objects.filter(user=user)
    wishlist_count = WishlistItem.objects.filter(wishlist__user=user).count()
    alerts_count = PriceAlert.objects.filter(user=user, is_active=True).count()

    context = {
        'profile': profile,
        'orders_count': orders.count(),
        'wishlist_count': wishlist_count,
        'alerts_count': alerts_count,
        'recent_orders': orders[:5]
    }
    return render(request, 'shopping/analytics.html', context)


# 9. Wishlist & Smart Wishlist
def wishlist_view(request):
    user, profile = _get_or_create_default_user()
    wishlist, _ = Wishlist.objects.get_or_create(user=user, title="My Primary Wishlist")
    items = wishlist.items.all()

    # Smart wishlist insights
    insights = []
    for item in items:
        pred = PricePredictorEngine.predict_buy_opportunity(item.product)
        if pred['recommendation'] == 'BUY NOW':
            insights.append(f"🔥 Price Alert: <strong>{item.product.title}</strong> is at its lowest price in 30 days!")

    return render(request, 'shopping/wishlist.html', {'wishlist': wishlist, 'items': items, 'insights': insights})


# 10. Cart & Checkout Assistant
def cart_view(request):
    user, profile = _get_or_create_default_user()
    cart, _ = Cart.objects.get_or_create(user=user)
    items = cart.items.all()

    # Check compatibility
    prods = [i.product for i in items]
    compatibility = CompatibilityEngine.check_compatibility(prods)

    # Effective breakdown
    total_effective = sum(float(i.subtotal) for i in items)
    coupon_savings = 2300.0 if total_effective > 10000 else 0.0
    final_amount = max(0.0, total_effective - coupon_savings)

    context = {
        'cart': cart,
        'items': items,
        'compatibility': compatibility,
        'total_effective': total_effective,
        'coupon_savings': coupon_savings,
        'final_amount': final_amount
    }
    return render(request, 'shopping/cart.html', context)


# 11. Visual Search View
def visual_search(request):
    user, profile = _get_or_create_default_user()
    results = None
    if request.method == 'POST':
        file_name = request.FILES.get('image_file').name if request.FILES.get('image_file') else "shoe_sample.jpg"
        results = VisualSearchEngine.search_by_image(file_name)

    return render(request, 'shopping/visual_search.html', {'results': results})


# API: Conversational Chat Endpoint
@csrf_exempt
def api_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    data = json.loads(request.body.decode('utf-8'))
    user_message = data.get('message', '')

    user, profile = _get_or_create_default_user()
    intent = IntentEngine.extract_intent(user_message)

    # Search & Rank products based on intent
    products = Product.objects.all()
    if intent.get('category') and intent['category'] != 'General':
        products = products.filter(category__name__icontains=intent['category'])

    scored = ScoringEngine.rank_and_badge_products(products, intent, profile.preference_weights)[:3]

    # Generate conversational AI response text
    reply_parts = []
    reply_parts.append(f"I understand your requirement! Category: **{intent['category']}**, Budget: **₹{intent.get('budget') or 80000:,.0f}**, Usage: **{', '.join(intent.get('usage', ['General']))}**.")

    if intent.get('is_bundle_query'):
        reply_parts.append("I have configured an optimized setup for your budget limit.")
    elif scored:
        top_prod = scored[0]['product']
        top_score = scored[0]['score']
        reply_parts.append(f"My #1 AI Recommendation is **{top_prod.title}** (Match Score: **{top_score}/100**).")

    products_json = []
    for s in scored:
        p = s['product']
        products_json.append({
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'price': float(s['effective_price']),
            'rating': p.rating,
            'badge': s['badge'],
            'score': s['score'],
            'image_url': p.image_url
        })

    return JsonResponse({
        'reply': " ".join(reply_parts),
        'intent': intent,
        'products': products_json
    })


# API: Add item to wishlist / cart
@csrf_exempt
def api_toggle_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        product_id = data.get('product_id')
        user, _ = _get_or_create_default_user()
        wishlist, _ = Wishlist.objects.get_or_create(user=user, title="My Primary Wishlist")
        product = get_object_or_404(Product, id=product_id)

        existing = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
        if existing:
            existing.delete()
            return JsonResponse({'status': 'removed'})
        else:
            WishlistItem.objects.create(wishlist=wishlist, product=product, added_price=product.base_price)
            return JsonResponse({'status': 'added'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def api_add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        product_id = data.get('product_id')
        user, _ = _get_or_create_default_user()
        cart, _ = Cart.objects.get_or_create(user=user)
        product = get_object_or_404(Product, id=product_id)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += 1
            item.save()

        return JsonResponse({'status': 'added', 'cart_count': cart.items.count()})
    return JsonResponse({'error': 'Invalid request'}, status=400)
