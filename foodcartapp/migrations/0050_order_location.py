# Generated by Django 3.2 on 2022-04-20 02:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
        ('foodcartapp', '0049_order_restaurant'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='location.place', verbose_name='Месторасположение'),
        ),
    ]
