from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='delivery-home'),
    path('about/', views.about, name='delivery-about'),
    path('catalog/', views.catalog, name='delivery-catalog'),
    path('product/<int:product_id>/', views.product_detail, name='delivery-product'),
    path('orders/', views.user_list, name='delivery-orders'),
    path('orders_manager/', views.manager_list, name='delivery-manager'),
    path('reset-filters/', views.reset_filters, name='reset_filters'),
    path('orders_courier/', views.courier_list, name='delivery-courier'),
    path('order/create', views.order_create, name='order_create'),
    path('order/success/', views.order_success, name='order_success'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('assign_manager/<int:order_id>/', views.assign_manager, name='assign_manager'),
    path('assign_courier/<int:order_id>/', views.assign_courier, name='assign_courier'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='order_cancel'),
]
