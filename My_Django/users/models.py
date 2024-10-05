from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from delivery.models import City


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    customer_name = models.CharField(max_length=100)  # получатель заказа по умолчанию
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)  # город
    address = models.CharField(max_length=100, blank=True)  # адрес доставки по умолчанию
    phone = models.CharField(max_length=100, blank=True)  # телефон по умолчанию
    is_manager = models.BooleanField(default=False)
    is_courier = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Определяем роли на основе групп
        self.is_manager = self.user.is_superuser or self.user.groups.filter(name='managers').exists()
        self.is_courier = self.user.is_superuser or self.user.groups.filter(name='couriers').exists()

        super().save(*args, **kwargs)

        # Обработка изображения после сохранения профиля
        self.save_image()

    def save_image(self):
        if self.image:
            img = Image.open(self.image)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
