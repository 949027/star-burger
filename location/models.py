import datetime
from django.db import models


class Place(models.Model):
    address = models.CharField('Адрес', max_length=200, unique=True)
    lat = models.DecimalField('Широта', max_digits=8, decimal_places=6)
    lon = models.DecimalField('Долгота', max_digits=8, decimal_places=6)
    update_date = models.DateTimeField(
        'Дата обновления',
        default=datetime.datetime.now,
    )

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'


