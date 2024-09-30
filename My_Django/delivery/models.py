import datetime

from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # пользователь
    city = models.ForeignKey(City, on_delete=models.CASCADE)  # город
    customer_name = models.CharField(max_length=100)  # получатель заказа
    address = models.CharField(max_length=100)  # адрес доставки
    customer_email = models.EmailField(max_length=100)  # email получателя
    phone = models.CharField(max_length=100)  # телефон
    items = models.TextField()  # список товаров заказа
    total_price = models.PositiveIntegerField()  # сумма заказа
    delivery_date = models.DateField()  # дата доставки
    is_new = models.BooleanField(default=True)  # новый
    created_date = models.DateTimeField(auto_now_add=True)  # дата создания заказа
    is_confirmed = models.BooleanField(default=False)  # подтверждён
    confirmation_date = models.DateTimeField(null=True, blank=True)  # дата подтверждения заказа
    is_delivered = models.BooleanField(default=False)  # доставлен
    is_delivered_time = models.TimeField(null=True, blank=True)  # время доставки
    is_canceled = models.BooleanField(default=False)  # отменён

    order_number = models.CharField(max_length=20, unique=True, editable=False)  # номер заказа

    def __str__(self):
        return f'Заказ #{self.order_number}'

    def save(self, *args, **kwargs):
        if self.is_new:
            current_date = timezone.now().strftime('%d%m%Y')
            city_abbreviation = self.city.abbreviation
            order_sequence = self._get_next_order_sequence(city_abbreviation)

            self.order_number = f"{city_abbreviation}-{current_date}-{order_sequence}"

        super().save(*args, **kwargs)

    def update_status(self):
        """Метод для обновления статуса заказа на основе текущих полей."""
        if self.is_canceled:
            self.is_new = False
            self.is_confirmed = False
            self.is_delivered = False
        elif self.is_confirmed:
            self.is_new = False
            self.confirmation_date = timezone.now()
        elif self.is_delivered:
            self.is_new = False
            self.is_confirmed = True
            self.is_delivered_time = timezone.now().time()

        # Сохраняем изменения в базе данных
        self.save()

    def _get_next_order_sequence(self, city_abbreviation):
        # Получаем последний номер заказа для данного города
        last_order = Order.objects.filter(city=self.city).order_by('created_date').last()
        if last_order:
            last_sequence = int(last_order.order_number.split('-')[-1])
            return str(last_sequence + 1).zfill(3)  # Заполняем нулями до трех цифр
        return '001'  # Начальный номер
