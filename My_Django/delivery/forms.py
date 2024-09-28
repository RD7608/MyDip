from django import forms
from .models import Order, City


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'city', 'address', 'delivery_date', 'phone']
        labels = {'customer_name': 'Имя покупателя', 'customer_email': 'Email покупателя',
                  'address': 'Адрес доставки', 'delivery_date': 'Дата доставки', 'phone': 'Телефон'}

        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}, ),
            'customer_email': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control'}, format='%d-%m-%Y'),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Выберите", required=True, label="Город доставки")

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'quantity'}))
