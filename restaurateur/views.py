from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.utils.http import url_has_allowed_host_and_scheme
from geopy import distance
import requests

from foodcartapp.models import Product, Restaurant, Order
from django.conf import settings


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    unprocessed_orders = Order.objects.filter(status='new')\
        .calculate_total_price()
    restaurants = Restaurant.objects.all()

    for order in unprocessed_orders:
        client_coordinates = fetch_coordinates(settings.APIKEY, order.address)
        suggested_restaurants = []
        order_product_set = set()
        for product_item in order.products.select_related('product').all():
            order_product_set.add(product_item.product)

        for restaurant in restaurants:
            restaurant_product_set = set()
            for product_item in restaurant.menu_items.select_related('product').all():
                restaurant_product_set.add(product_item.product)

            if restaurant_product_set.union(order_product_set) == restaurant_product_set:
                restaurant_coordinates = fetch_coordinates(
                    settings.APIKEY,
                    restaurant.address
                )
                restaurant.distance = round(distance.distance(
                    client_coordinates,
                    restaurant_coordinates
                ).km, 2)
                suggested_restaurants.append(
                    (restaurant.name, restaurant.distance)
                )
        order.suggested_restaurants = sorted(
            suggested_restaurants,
            key=lambda i: i[1]
        )

    return render(request, template_name='order_items.html', context={
        'unprocessed_orders': unprocessed_orders,
        'redirect_url': request.path if url_has_allowed_host_and_scheme(
            request.path,
            settings.ALLOWED_HOSTS,
        ) else ''
    })
