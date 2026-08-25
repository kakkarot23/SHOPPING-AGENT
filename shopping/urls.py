from django.urls import path
from shopping import views

urlpatterns = [
    # Pages
    path('', views.command_center, name='command_center'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('compare/', views.compare, name='compare'),
    path('gift-finder/', views.gift_finder, name='gift_finder'),
    path('bundle-builder/', views.bundle_builder, name='bundle_builder'),
    path('autopilot/', views.autopilot, name='autopilot'),
    path('analytics/', views.analytics, name='analytics'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('cart/', views.cart_view, name='cart'),
    path('visual-search/', views.visual_search, name='visual_search'),

    # API Endpoints
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/wishlist/toggle/', views.api_toggle_wishlist, name='api_toggle_wishlist'),
    path('api/cart/add/', views.api_add_to_cart, name='api_add_to_cart'),
]
