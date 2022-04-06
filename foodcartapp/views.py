from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Product, Order, ProductItem


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


@api_view(['POST'])
def register_order(request):
    incoming_order = request.data

    if not incoming_order.get('products') \
        or not incoming_order['products'] \
        or not isinstance(incoming_order['products'], list):
            return Response({'error': 'products key not present or not list'})

    order = Order.objects.create(
        firstname=incoming_order['firstname'],
        lastname=incoming_order['lastname'],
        address=incoming_order['address'],
        phonenumber=incoming_order['phonenumber'],
    )
    for product_item in incoming_order['products']:
        product = Product.objects.get(id=product_item['product'])
        ProductItem.objects.create(
            order=order,
            product=product,
            amount=product_item['quantity'],
        )
    return Response({})
