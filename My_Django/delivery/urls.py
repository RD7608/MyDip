from django.urls import path
from . import views
from .views import HomeView, AboutView, CatalogView, ProductDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='delivery-home'),
    path('about/', AboutView.as_view(), name='delivery-about'),
    path('catalog/', CatalogView.as_view(), name='delivery-catalog'),
    path('catalog/product/<int:product_id>/', ProductDetailView.as_view(), name='delivery-product'),
    path('order/create/', views.order_create, name='order_create'),
    path('order/success/', views.order_success, name='order_success'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('orders/', views.orders_list, name='delivery-orders'),
    path('orders/manager/', views.manager_list, name='delivery-manager'),
    path('orders/manager/assign_courier/<int:order_id>/', views.assign_courier, name='assign_courier'),
    path('orders/manager/cancel_order/<int:order_id>/', views.cancel_order, name='order_cancel'),
    path('orders/courier/', views.courier_list, name='delivery-courier'),
    path('orders/courier/confirm_delivery/<int:order_id>/', views.confirm_delivery, name='confirm_delivery'),
]
