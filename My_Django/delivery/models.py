from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='static/product_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # пользователь
    city = models.ForeignKey(City, on_delete=models.CASCADE)  # город
    customer_name = models.CharField(max_length=100)  # получатель заказа
    address = models.CharField(max_length=100)  # адрес доставки
    customer_email = models.EmailField(max_length=100)  # email получателя
    total_price = models.PositiveIntegerField()  # сумма заказа
    phone = models.CharField(max_length=100)  # телефон
    created_date = models.DateTimeField(auto_now_add=True)  # дата создания заказа
    confirmation_date = models.DateTimeField(default=None)  # дата подтверждения заказа
    order_number = models.UUIDField(unique=True, editable=False)  # номер заказа
    delivery_date = models.DateField()  # дата доставки
    is_new = models.BooleanField(default=True)  # новый
    is_confirmed = models.BooleanField(default=False)  # подтверждён
    is_delivered = models.BooleanField(default=False)  # доставлен
    is_canceled = models.BooleanField(default=False)  # отменён

    def __str__(self):
        return str(self.order_number)  # номер заказа

    def save(self, *args, **kwargs):
        if self.is_new:
            self.order_number = self.generate_order_number()

        if self.is_confirmed:
            self.confirmation_date = timezone.now()
            self.is_new = False
            self.is_confirmed = True

        if self.is_delivered:
            self.delivery_date = timezone.now().date()
            self.is_delivered = True

        if self.is_canceled:
            self.is_canceled = True

        super().save(*args, **kwargs)

    def generate_order_number(self):
        from uuid import uuid4
        return uuid4()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # заказ
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # количество
    price = models.PositiveIntegerField()  # цена за единицу


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
