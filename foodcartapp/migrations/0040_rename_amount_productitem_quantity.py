# Generated by Django 3.2 on 2022-04-07 05:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_alter_productitem_order'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productitem',
            old_name='amount',
            new_name='quantity',
        ),
    ]