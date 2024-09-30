from django.core.exceptions import ValidationError
from django.utils.html import format_html
import re

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Order , City


class OrderForm ( forms.ModelForm ):
    class Meta:
        model = Order
        fields = ['customer_name' , 'customer_email' , 'city' , 'address' , 'delivery_date' , 'phone']
        labels = {'customer_name': 'Имя покупателя' , 'customer_email': 'Email покупателя' ,
                  'address': 'Адрес доставки' , 'delivery_date': 'Дата доставки' , 'phone': 'Телефон'}

        widgets = {
            'customer_name': forms.TextInput ( attrs={'class': 'form-control'} , ) ,
            'customer_email': forms.TextInput ( attrs={'class': 'form-control'} ) ,
            'delivery_date': forms.DateInput ( attrs={'class': 'form-control' , 'type': 'date'} ) ,
            'address': forms.TextInput ( attrs={'class': 'form-control'} ) ,
            'phone': forms.TextInput ( attrs={'class': 'form-control'} ) ,
        }

    city = forms.ModelChoiceField ( queryset=City.objects.all () , empty_label="Выберите" , required=True ,
                                    label="Город доставки" )

    def __init__(self , *args , **kwargs):
        super ( OrderForm , self ).__init__ ( *args , **kwargs )
        self.fields[
            'delivery_date'].initial = timezone.now ().date ()  # Устанавливаем текущую дату, если время меньше 10:00

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data.get ( 'delivery_date' )

        now = timezone.now ()
        current_time = now.time ()

        if current_time < timezone.datetime.strptime ( "10:00" , "%H:%M" ).time ():
            # Если текущее время меньше 10:00, устанавливаем дату доставки на сегодня
            if delivery_date >= now.date ():
                return delivery_date
            else:
                raise forms.ValidationError ( format_html (
                    "Дата доставки не может быть раньше сегодняшнего дня. Смотри <a href='{url}'>график доставки</a>" ,
                    url='/about/' ) )
        else:
            # Если текущее время больше или равно 10:00, устанавливаем дату на завтра
            if delivery_date < (now + timezone.timedelta ( days=1 )).date ():
                raise forms.ValidationError ( format_html (
                    "Дата доставки не может быть ранее завтрашнего дня. Смотри <a href='{url}'>график доставки</a>" ,
                    url='/about/' ) )
            return delivery_date

    def clean_phone(self):
        phone = self.cleaned_data.get ( 'phone' )
        # Регулярное выражение для проверки формата телефона
        phone_pattern = re.compile ( r'^\+?[0-9\s-]{7,15}$' )  # пример: +123 456 789 0123
        if phone:
            if not phone_pattern.match ( phone ):
                raise forms.ValidationError (
                    "Телефон номер должен быть в правильном формате. Пример: +123 456 789 0123" )
        return phone


'''
    def __init__(self , *args , **kwargs):
        super ( OrderForm , self ).__init__ ( *args , **kwargs )
        now = timezone.now ()
        if now.hour < 10:
            self.fields['delivery_date'].initial = now.date ()  # Устанавливаем текущую дату, если время меньше 10:00
        else:
            self.fields['delivery_date'].initial = now.date () + timezone.timedelta (
                days=1 )  # Устанавливаем завтрашнюю дату

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data.get ( 'delivery_date' )

        now = timezone.now ()
        current_time = now.time ()

        if current_time < timezone.datetime.strptime ( "10:00" , "%H:%M" ).time ():
            # Если текущее время меньше 10:00, устанавливаем дату доставки на сегодня
            if delivery_date < now.date ():
                raise forms.ValidationError ( "Дата доставки не может быть раньше сегодняшнего дня." )
            return now.date ()
        else:
            # Если текущее время больше или равно 10:00, устанавливаем дату на завтра
            if delivery_date < (now + timezone.timedelta ( days=1 )).date ():
                raise forms.ValidationError ( "Дата доставки не может быть ранее завтрашнего дня." )
            return delivery_date
'''


class CartAddProductForm ( forms.Form ):
    quantity = forms.IntegerField ( min_value=1 , initial=1 , widget=forms.NumberInput ( attrs={'class': 'quantity'} ) )
