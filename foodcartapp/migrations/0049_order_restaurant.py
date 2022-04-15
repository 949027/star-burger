# Generated by Django 3.2 on 2022-04-14 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20220413_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='foodcartapp.restaurant', verbose_name='Ресторан'),
        ),
    ]
