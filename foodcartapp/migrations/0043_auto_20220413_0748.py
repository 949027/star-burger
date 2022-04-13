# Generated by Django 3.2 on 2022-04-13 07:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_auto_20220412_0220'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='processed',
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('new', 'Необработанный'), ('processed', 'Обработан'), ('cooking', 'Готовится'), ('ready', 'Готов')], default='new', max_length=20, verbose_name='Статус заказа'),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Стоимость'),
        ),
    ]