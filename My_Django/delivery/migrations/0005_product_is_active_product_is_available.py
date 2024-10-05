# Generated by Django 5.1.1 on 2024-10-05 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0004_order_courier_order_manager'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_available',
            field=models.BooleanField(default=False),
        ),
    ]
