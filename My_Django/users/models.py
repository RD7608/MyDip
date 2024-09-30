from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from delivery.models import City


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    customer_name = models.CharField(max_length=100)  # получатель заказа по умолчанию
    city = models.ForeignKey(City, on_delete=models.CASCADE)  # город
    address = models.CharField(max_length=100, blank=True) # адрес доставки по умолчанию
    phone = models.CharField(max_length=100, blank=True) # телефон по умолчанию

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)