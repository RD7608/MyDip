from django.shortcuts import render , get_object_or_404 , redirect
from .models import Product , Order
from .forms import OrderForm
from django.urls import reverse

products = Product.objects.all ()


def home(request):
    cart = request.session.get ( 'cart' , {} )  # Получаем корзину
    cart_items_count = request.session.get ( 'cart_items_count' , 0 )  # Количество товаров в корзине
    product_items = []
    total_price = 0  # Общая сумма

    for product in products:
        try:
            product_quantity = cart[str ( product.id )]  # Получаем количество товаров
        except:
            product_quantity = 0

        # Добавляем в список детали продукта
        product_items.append ( {
            'product': product ,
            'quantity': product_quantity ,
        } )

    context = {
        'product_items': product_items ,
        'cart_items_count': cart_items_count ,  # Количество товаров в корзине
    }
    return render ( request , 'delivery/home.html' , context )


def about(request):
    return render ( request , 'delivery/about.html' , {'title': 'О доставке'} )


def news(request):
    return render ( request , 'delivery/news.html' , {'title': 'Новости'} )


def order(request):
    return render ( request , 'delivery/order.html' , {'title': 'Заказы'} )


# Оформление заказа
def order_create(request):
    cart = request.session.get ( 'cart' , {} )
    products = Product.objects.filter ( id__in=cart.keys () )
    cart_items_count = request.session.get ( 'cart_items_count' , 0 )  # Количество товаров в корзине
    total_price = 0
    if request.method == 'POST':
        form = OrderForm ( request.POST )
        if form.is_valid ():
            order = form.save ( commit=False )
            order.total_price = total_price
            order.save ()
            # Очистка корзины после оформления заказа
            request.session['cart'] = {}
            return redirect ( 'order_success' )  # Направление на страницу успеха
    else:
        form = OrderForm ()

    context = {
        'form': form ,
        'products': products ,
        'total_price': total_price ,
        'cart_items_count': cart_items_count ,
    }

    return render ( request , 'delivery/order_form.html' , context )


def order_success(request):
    return render ( request , 'delivery/order_success.html' )


# Добавление товара в корзину
def add_to_cart(request , product_id):
    cart = request.session.get ( 'cart' , {} )  # получаем корзину из сессии
    product_id = str ( product_id )
    # Добавить товар в корзину
    if product_id in cart:
        cart[product_id] += 1  # Увеличиваем количество товара
    else:
        cart[product_id] = 1  # Добавляем новый товар

    request.session['cart'] = cart  # Обновляем количество товаров в корзине
    request.session['cart_items_count'] = sum ( cart.values () )  # Обновляем общее количество

    return redirect ( reverse ( 'delivery-home' ) )


# Отображение корзины
def cart_view(request):
    # Получаем корзину из сессии
    cart = request.session.get ( 'cart' , {} )

    # Находим все продукты, соответствующие ID в корзине
    products = Product.objects.filter ( id__in=cart.keys () )

    cart_items = []  # Список для хранения деталей продуктов в корзине
    total_price = 0  # Общая сумма

    for product in products:
        product_quantity = cart[str ( product.id )]  # Получаем количество товаров
        product_total_price = product.price * product_quantity  # Считаем сумму для этого продукта

        # Добавляем в список детали продукта
        cart_items.append ( {
            'product': product ,
            'quantity': product_quantity ,
            'total_price': product_total_price
        } )

        # Добавляем к общей сумме
        total_price += product_total_price

    # Обработка пост-запросов на изменение количества или удаление
    if request.method == "POST":
        if 'update_quantity' in request.POST:
            product_id = request.POST.get ( 'product_id' )
            new_quantity = int ( request.POST.get ( 'quantity' ) )
            if new_quantity > 0:
                cart[product_id] = new_quantity  # Обновляем количество
            else:
                del cart[product_id]  # Удаляем продукт, если количество <= 0
            request.session['cart'] = cart
            request.session['cart_items_count'] = sum ( cart.values () )
            return redirect ( 'cart_view' )

        elif 'remove_item' in request.POST:
            product_id = request.POST.get ( 'product_id' )
            if product_id in cart:
                del cart[product_id]  # Удаляем продукт из корзины
            request.session['cart'] = cart
            request.session['cart_items_count'] = sum ( cart.values () )
            return redirect ( 'cart_view' )

    cart_items_count = request.session.get ( 'cart_items_count' , 0 )
    # Передаем данные в шаблон
    context = {
        'cart_items': cart_items ,
        'total_price': total_price ,
        'cart_items_count': cart_items_count ,
    }

    return render ( request , 'delivery/cart.html' , context )


def update_cart(request , product_id):
    cart = request.session.get ( 'cart' , {} )
    product_id = str ( product_id )
    # Получаем текущее количество товара
    current_quantity = cart.get ( product_id , 0 )

    if request.method == 'POST':
        action = request.POST.get ( 'action' )
        if action == 'increment':
            cart[product_id] = current_quantity + 1
        elif action == 'decrement' and current_quantity > 0:
            cart[product_id] = current_quantity - 1

        # Удаляем товар из корзины, если его количество стало 0
        if cart[product_id] <= 0:
            del cart[product_id]

    request.session['cart'] = cart
    request.session['cart_items_count'] = sum ( cart.values () )

    return redirect ( 'delivery-home' )
