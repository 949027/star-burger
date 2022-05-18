import datetime

from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum

from location.models import Place


class ProductItem(models.Model):
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='product_items',
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        verbose_name='Продукт',
        related_name='items',
    )
    quantity = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        'Стоимость',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )


class OrderQuerySet(models.QuerySet):

    def calculate_prices(self):
        return self.annotate(
            total_price=Sum(F('product_items__quantity') * F('product_items__price'))
        )

    def suggest_restaurants(self):
        orders = self.prefetch_related('product_items__product')
        restaurants = Restaurant.objects.prefetch_related('menu_items__product').all()
        for order in orders:
            suggested_restaurants = []
            order_product_set = set()
            for product_item in order.product_items.all():
                order_product_set.add(product_item.product)

            for restaurant in restaurants:
                restaurant_product_set = set()
                for product_item in restaurant.menu_items.all():
                    restaurant_product_set.add(product_item.product)

                if restaurant_product_set.union(order_product_set) == restaurant_product_set:
                    suggested_restaurants.append(restaurant)

                order.suggested_restaurants = suggested_restaurants
        return orders


class Order(models.Model):
    firstname = models.CharField(
        'Имя',
        max_length=50
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=50
    )
    phonenumber = PhoneNumberField('Телефон', db_index=True)
    address = models.CharField('Адрес', max_length=200)
    place = models.ForeignKey(
        Place,
        verbose_name='Месторасположение',
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField(
        'Статус заказа',
        max_length=20,
        db_index=True,
        default='new',
        choices=(('new', 'Необработанный'), ('processed', 'Обработан'),
                 ('cooking', 'Готовится'), ('ready', 'Готов'))
    )
    payment_type = models.CharField(
        'Способ оплаты',
        max_length=20,
        db_index=True,
        choices=(
            ('cash', 'Наличные'),
            ('card', 'Банковская карта')
        )
    )
    restaurant = models.ForeignKey(
        'Restaurant',
        verbose_name='Ресторан',
        related_name='orders',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    registrated_at = models.DateTimeField(
        'Заказ зарегистрирован в',
        default=datetime.datetime.now,
        db_index=True,
    )
    called_at = models.DateTimeField('Звонок в', blank=True, null=True)
    delivered_at = models.DateTimeField('Доставлено в', blank=True, null=True)

    objects = OrderQuerySet.as_manager()

    def str(self):
        return f'{self.id} - {self.address}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    place = models.ForeignKey(
        Place,
        verbose_name='Месторасположение',
        related_name='restaurants',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"
