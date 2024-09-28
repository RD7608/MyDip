from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order
from .forms import OrderForm
from django.urls import reverse

products = Product.objects.all()


def home(request):
    context = {
        'products': products
    }
    return render(request, 'delivery/home.html', context)


def about(request):
    return render(request, 'delivery/about.html', {'title': 'О доставке'})


def news(request):
    return render(request, 'delivery/news.html', {'title': 'Новости'})


def order(request):
    return render(request, 'delivery/order.html', {'title': 'Заказы'})


# Оформление заказа
def order_create(request):
    form = OrderForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('order_success')

    context = {
        'form': form,
        'title': 'Оформление заказа'
    }

    return render(request, 'delivery/order_form.html', context)


def order_success(request):
    return render(request, 'delivery/order_success.html')


# Добавление товара в корзину
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart
    return redirect(reverse('delivery-home'))


# Удаление товара из корзины
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
    request.session['cart'] = cart
    return redirect(reverse('cart'))


# Отображение корзины
def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    total_price = sum(product.price * cart[str(product.id)] for product in products)

    if request.method == 'POST':
        for product_id, quantity in request.POST.items():
            if product_id in cart:
                cart[product_id] = int(quantity)

        request.session['cart'] = cart
        print(cart)

    return render(request, 'delivery/cart.html', {'products': products, 'cart': cart, 'total_price': total_price})
