from django.urls import path
from .views import (
    ProductsView,
    HomeView,
    ProductDetailView,
    CartView,
    CheckoutView,
    PaymentView,
    add_to_cart,
    remove_from_cart,
    remove_single_item,
    RequestRefundView,
    ProfileOrderView,
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('products/', ProductsView.as_view(), name='products'),
    path('products/<slug>', ProductDetailView.as_view(), name='product'),
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_method>', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('profile/orders/', ProfileOrderView.as_view(), name='my-orders'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item/<slug>',
         remove_single_item, name='remove-single-item'),
]
