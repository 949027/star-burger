# Generated by Django 3.2 on 2022-04-13 10:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='registrated_at',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Заказ зарегистрирован в'),
        ),
    ]
