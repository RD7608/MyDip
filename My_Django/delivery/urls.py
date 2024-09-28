from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='delivery-home'),
    path('about/', views.about, name='delivery-about'),
    path('news/', views.news, name='delivery-news'),
    path('order/', views.order, name='delivery-order'),
    path('order/create', views.order_create, name='order_create'),
    path('order/success/', views.order_success, name='order_success'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/', views.cart_view, name='cart_view'),
]
