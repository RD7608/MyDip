from django.test import TestCase
from django.urls import reverse
from .models import User, Order

class OrderTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_order_list_view(self):
        response = self.client.get(reverse('delivery-order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delivery/orders.html')


