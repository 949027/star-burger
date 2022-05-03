from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ListField
import requests

from .models import Product, Order, ProductItem
from location.models import Place


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class ProductItemSerializer(ModelSerializer):
    class Meta:
        model = ProductItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ListField(child=ProductItemSerializer(),
                         allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname',
                  'phonenumber', 'address', 'products']


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    incoming_order = request.data

    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    client_coordinates = fetch_coordinates(
        settings.YANDEX_API_KEY,
        incoming_order['address']
    )
    if client_coordinates:
        place, _ = Place.objects.get_or_create(
            address=incoming_order['address'],
            lat=client_coordinates[0],
            lon=client_coordinates[1],
        )
    else:
        place = None

    order = Order.objects.create(
        firstname=incoming_order['firstname'],
        lastname=incoming_order['lastname'],
        address=incoming_order['address'],
        location=place,
        phonenumber=incoming_order['phonenumber'],
    )
    for product_item in incoming_order['products']:
        product = Product.objects.get(id=product_item['product'])
        ProductItem.objects.create(
            order=order,
            product=product,
            quantity=product_item['quantity'],
        )
    serializer = OrderSerializer(order)

    return Response(serializer.data)
