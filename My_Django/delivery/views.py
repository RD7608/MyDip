from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, City
from .forms import OrderForm
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages


def home(request):
    cart = request.session.get('cart', {})  # Получаем корзину
    cart_items_count = request.session.get('cart_items_count', 0)  # Количество товаров в корзине
    products = Product.objects.filter(is_available=True)
    product_items = []

    # Проходим по всем продуктам и собираем информацию о них
    for product in products:
        product_id = str(product.id)  # Приводим ID товара к строке
        product_quantity = cart.get(product_id, 0)  # Получаем количество товаров, если его нет, возвращаем 0

        # Добавляем в список детали продукта
        product_items.append({
            'product': product,
            'quantity': product_quantity,
        })

    context = {
        'product_items': product_items,
        'cart_items_count': cart_items_count,  # Количество товаров в корзине
    }
    return render(request, 'delivery/home.html', context)


def about(request):
    return render(request, 'delivery/about.html', {'title': 'Информация'})


def catalog(request):
    messages = request.session.get('messages', [])
    products = Product.objects.filter(is_active=True)
    cart_items_count = request.session.get('cart_items_count', 0)
    context = {
        "request": request,
        "messages": messages,
        "products": products,
        "cart_items_count": cart_items_count,
        "title": "Каталог"
    }

    return render(request, 'delivery/catalog.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_items_count = request.session.get('cart_items_count', 0)  # Количество товаров в корзине
    context = {
        'product': product,
        'cart_items_count': cart_items_count,
        'title': product.name,
    }
    return render(request, 'delivery/product.html', context)


@login_required
def user_list(request):
    cart_items_count = request.session.get('cart_items_count', 0)  # Количество товаров в корзине
    orders = Order.objects.filter(user=request.user)
    context = {
        'title': 'Заказы',
        'orders': orders,
        'cart_items_count': cart_items_count,
    }

    return render(request, 'delivery/orders.html', context)


@login_required
def manager_list(request):
    cart_items_count = request.session.get('cart_items_count', 0)
    if request.user.profile.is_manager:
        # Сохрание фильтров в сессию
        if request.method == 'GET':
            if request.GET.get('reset'):
                request.session['date_filter'] = None
                request.session['city_filter'] = "all"
                request.session['manager_filter'] = "no_manager"
            else:
                request.session['date_filter'] = request.GET.get('date', str(timezone.now().date()))
                request.session['city_filter'] = request.GET.get('city', 'all')
                request.session['manager_filter'] = request.GET.get('manager', 'no_manager')

        # Получение сохраненных значений фильтров из сессии
        date_filter = request.session.get('date_filter', str(timezone.now().date()))
        city_filter = request.session.get('city_filter', 'all')
        manager_filter = request.session.get('manager_filter', 'no_manager')

        orders = Order.objects.filter(is_confirmed=True, is_canceled=False)

        # Получаем доступные города
        cities = City.objects.all()

        # Фильтрация по дате
        if date_filter:
            orders = orders.filter(delivery_date=date_filter)

        # Фильтрация по городу
        if city_filter and city_filter != 'all':
            orders = orders.filter(city__id=city_filter)

        # Фильтрация по менеджеру
        if manager_filter == 'my_orders':
            orders = orders.filter(manager=request.user)

        couriers = User.objects.filter(profile__is_courier=True)

        context = {
            'title': 'Список заказов менеджера',
            'orders': orders,
            'cart_items_count': cart_items_count,
            'couriers': couriers,
            'cities': cities,
            'date_filter': date_filter,
            'city_filter': city_filter,
            'manager_filter': manager_filter,
        }
    else:
        return redirect('/')

    return render(request, 'delivery/orders_manager.html', context)

@login_required
def courier_list(request):
    cart_items_count = request.session.get('cart_items_count', 0)  # Количество товаров в корзине
    if request.user.profile.is_courier:
        orders = Order.objects.filter(courier=request.user)
        context = {
            'title': 'Заказы',
            'orders': orders,
            'cart_items_count': cart_items_count,
        }
    else:
        context = {
            'title': 'Заказы',
            'message': {"text": "Вы не являетесь курьером!"},
            'cart_items_count': cart_items_count,
        }
    return render(request, 'delivery/orders.html', context)


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)


# Оформление заказа
def order_create(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items_count = request.session.get('cart_items_count', 0)  # Количество товаров в корзине
    cart_items = []  # Список для хранения деталей продуктов в корзине
    total_price = 0  # Общая сумма
    for product in products:
        product_quantity = cart[str(product.id)]  # Получаем количество товаров
        product_total_price = product.price * product_quantity  # Считаем сумму для этого продукта

        # Добавляем в список детали продукта
        cart_items.append({
            'product': product,
            'quantity': product_quantity,
            'total_price': product_total_price
        })

        # Добавляем к общей сумме
        total_price += product_total_price

    # Получение пользователя "anonymous"
    anon_user = User.objects.get(username='anonymous')

    if request.user.is_authenticated:
        user = request.user
    else:
        user = anon_user  # Используется пользователь "anonymous"

    if request.method == 'POST':
        form = OrderForm(request.POST, user=user)
        # Обработка формы заказа
        if form.is_valid():
            order = form.save(commit=False)
            order.total_price = total_price
            order.created_date = timezone.now()  # Устанавливаем дату создания
            order.user = user
            order.items = cart
            order.save()

            order.is_confirmed = True  # Ставим статус подтвержден
            order.update_status()  # Обновляем статусы на основе изменений
            # Очистка корзины после оформления заказа
            request.session['cart'] = {}
            request.session['cart_items_count'] = 0
            return redirect(reverse('order_success') + '?action=create&order_id=' + str(order.id))
    else:
        form = OrderForm(user=user)

    context = {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_items_count': cart_items_count,
        'title': 'Оформление заказа',
    }

    return render(request, 'delivery/order_form.html', context)


def order_success(request):
    action = request.GET.get('action')
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if action == 'create':
        message = "Заказ успешно создан!"
    elif action == 'confirm':
        message = "Заказ успешно подтверждён!"
    else:
        message = "Неизвестное действие."

    return render(request, 'delivery/order_success.html', {'message': message, 'order': order, 'title': 'Заказ'})


# Отображение корзины
def cart_view(request):
    # Получаем корзину из сессии
    cart = request.session.get('cart', {})

    # Находим все продукты, соответствующие ID в корзине
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []  # Список для хранения деталей продуктов в корзине
    total_price = 0  # Общая сумма

    for product in products:
        product_quantity = cart[str(product.id)]  # Получаем количество товаров
        product_total_price = product.price * product_quantity  # Считаем сумму для этого продукта

        # Добавляем в список детали продукта
        cart_items.append({
            'product': product,
            'quantity': product_quantity,
            'total_price': product_total_price
        })

        # Добавляем к общей сумме
        total_price += product_total_price

    # Обработка пост-запросов на изменение количества или удаление
    if request.method == "POST":
        if 'update_quantity' in request.POST:
            product_id = request.POST.get('product_id')
            new_quantity = int(request.POST.get('quantity'))
            if new_quantity > 0:
                cart[product_id] = new_quantity  # Обновляем количество
            else:
                del cart[product_id]  # Удаляем продукт, если количество <= 0
            request.session['cart'] = cart
            request.session['cart_items_count'] = sum(cart.values())
            return redirect('cart_view')

        elif 'remove_item' in request.POST:
            product_id = request.POST.get('product_id')
            if product_id in cart:
                del cart[product_id]  # Удаляем продукт из корзины
            request.session['cart'] = cart
            request.session['cart_items_count'] = sum(cart.values())
            return redirect('cart_view')

        elif 'order_create' in request.POST:
            request.session['cart'] = cart
            request.session['cart_items_count'] = sum(cart.values())
            return redirect('order_create')

    request.session['cart_items_count'] = sum(cart.values())
    cart_items_count = request.session.get('cart_items_count', 0)
    # Передаем данные в шаблон
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_items_count': cart_items_count,
        'title': 'Корзина',
    }

    return render(request, 'delivery/cart.html', context)


def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    # Получаем текущее количество товара
    current_quantity = cart.get(product_id, 0)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increment':
            cart[product_id] = current_quantity + 1
        elif action == 'decrement' and current_quantity > 0:
            cart[product_id] = current_quantity - 1
        elif action == 'add':
            cart[product_id] = 1

        # Удаляем товар из корзины, если его количество стало 0
        if cart[product_id] <= 0:
            del cart[product_id]

    request.session['cart'] = cart
    request.session['cart_items_count'] = sum(cart.values())

    return redirect('delivery-home')


@login_required
def assign_manager(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        if request.user.profile.is_manager:
            manager_id = request.POST.get('manager')
            if manager_id:
                order.courier = User.objects.get(id=manager_id)
            order.save()
            return redirect('delivery-manager')


@login_required
def assign_courier(request, order_id):
    if request.method == 'POST':
        courier_id = request.POST.get('courier_id')
        try:
            order = Order.objects.get(id=order_id)
            courier = User.objects.get(id=courier_id)
            order.courier = courier  # Назначение курьера
            order.manager = request.user  # Назначение текущего пользователя менеджером
            order.save()
            messages.success(request, 'Курьер назначен успешно.')
        except Order.DoesNotExist:
            messages.error(request, 'Заказ не найден.')
        except User.DoesNotExist:
            messages.error(request, 'Курьер не найден.')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')

    return redirect('delivery-manager')


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST' and request.user.profile.is_manager:
        order.is_canceled = True
        order.save()
        return redirect('delivery-manager')


def reset_filters(request):
    # Удаляем фильтры из сессии или запроса
    if 'date_filter' in request.session:
        del request.session['date_filter']

    messages.success(request, 'Фильтры успешно сброшены.')
    return redirect('delivery-manager')