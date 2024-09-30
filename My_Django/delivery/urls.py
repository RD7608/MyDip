from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='delivery-home'),
    path('about/', views.about, name='delivery-about'),
    path('news/', views.news, name='delivery-news'),
    path('catalog/', views.order_list, name='delivery-catalog'),
    path('order/', views.order_list, name='delivery-order'),
    path('order/create', views.order_create, name='order_create'),
    path('order/success/', views.order_success, name='order_success'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
]
