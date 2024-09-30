from django.core.exceptions import ValidationError
from django.utils.html import format_html
import re

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Order, City


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'city', 'address', 'delivery_date', 'phone']
        labels = {'customer_name': 'Имя получателя', 'customer_email': 'Email заказчика',
                  'address': 'Адрес доставки', 'delivery_date': 'Дата доставки', 'phone': 'Телефон'}

        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}, ),
            'customer_email': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Выберите", required=True,
                                  label="Город доставки")

    def __init__(self, *args, user=None, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['delivery_date'].initial = timezone.now().date()

        if user.username != "anonymous":
            self.fields['customer_name'].initial = user.profile.customer_name
            self.fields['customer_email'].initial = user.email
            self.fields['city'].initial = user.profile.city
            self.fields['address'].initial = user.profile.address
            self.fields['phone'].initial = user.profile.phone

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data.get('delivery_date')

        now = timezone.now()
        current_time = now.time()

        # Проверка, что дата доставки не является воскресеньем
        if delivery_date and delivery_date.weekday() == 6:  # Воскресенье
            raise ValidationError("Дата доставки не может быть в воскресенье.")

        elif current_time < timezone.datetime.strptime("10:00", "%H:%M").time():
            # Если текущее время меньше 10:00, проверяем дату доставки не раньше сегодня
            if delivery_date < now.date():
                raise ValidationError("Дата доставки не может быть раньше сегодняшнего дня.")
        else:
            # Если текущее время больше или равно 10:00, проверяем дату не раньше завтра
            if delivery_date < (now + timezone.timedelta(days=1)).date():
                raise ValidationError("Дата доставки не может быть ранее завтрашнего дня.")
        return delivery_date

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Регулярное выражение для проверки формата телефона
        phone_pattern = re.compile(r'^\+?[0-9\s-]{7,15}$')  # пример: +123 456 789 0123
        if phone:
            if not phone_pattern.match(phone):
                raise forms.ValidationError(
                    "Телефон номер должен быть в правильном формате. Пример: +123 456 789 0123")
        return phone


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'quantity'}))
