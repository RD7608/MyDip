# Generated by Django 5.1.1 on 2024-09-30 18:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0003_alter_product_image'),
        ('users', '0002_profile_address_profile_city_profile_customer_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='delivery.city'),
        ),
    ]
