from telebot import types
import requests
from decouple import config
import re
from typing import Dict, Tuple, List, Union
import logging
from .history import num_nights

__all__ = ['get_cities_from_rapidapi', 'get_hotels_from_rapidapi', 'get_photos_from_rapidapi']

log = logging.getLogger(__name__)


def get_cities_from_rapidapi(city: str) -> Union[Dict[str, str], str]:
    """
    Функция, которая принимает строку и ищет на rapidapi все города с совпадением по строке.
    Возвращает словарь - id города: название
    :param city: искомый город
    """

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config('x-rapidapi-key')
    }

    querystring_city = {"query": city, "locale": "ru_RU"}

    try:
        response = requests.request("GET", url, headers=headers, params=querystring_city, timeout=20).json()

        city_dct = dict()
        pattern_city = r"(.*)<.*?>(.+)</span>(.*)"
        for i_city in response['suggestions'][0]['entities']:
            if i_city['type'] == 'CITY':
                city = ''.join(re.findall(pattern_city, i_city['caption'])[0])
                city_dct[i_city["destinationId"]] = city
        return city_dct

    except (requests.exceptions.ConnectionError,  requests.exceptions.ReadTimeout, requests.exceptions.JSONDecodeError,
            TypeError, KeyError, IndexError) as error:   # мне попадалась эта ошибка, почему она подсвечена? requests.exceptions.JSONDecodeError
        log.error('Ошибка с получением города', exc_info=error)
        return 'Технические неполадки с сайтом, попробуйте еще раз.'


def get_hotels_from_rapidapi(data: Tuple) -> Union[Dict[int, dict[Union[str, str]]], str]:
    """
    Функция, которая по заданному запросу ищет отели на rapidapi.
    Возвращает словарь с данными отелей.
    :param data: данные для запроса
    """

    url = "https://hotels4.p.rapidapi.com/properties/list"
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config('x-rapidapi-key')
    }

    querystring_hotel = {"destinationId": data[0], "checkIn": data[1], "checkOut": data[2],
                         "pageSize": data[3], "pageNumber": "1", "adults1": "1", "sortOrder": "PRICE",
                         "locale": "ru_RU", "currency": "RUB"
                         }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring_hotel, timeout=20).json()

        hotel_dct = dict()
        nights = num_nights(data[1], data[2])
        for i_hotel in response['data']['body']['searchResults']['results']:
            i_hotel_dct = dict()
            distance = i_hotel['landmarks'][0]['distance']
            price = i_hotel['ratePlan']['price']['current']

            i_hotel_dct['Название отеля'] = i_hotel['name']
            i_hotel_dct['Адрес'] = i_hotel['address']['streetAddress']
            i_hotel_dct['Расстояние до центра'] = get_distance(distance)
            i_hotel_dct['Цена за ночь'] = i_hotel['ratePlan']['price']['current']
            i_hotel_dct[f'Цена за {nights} ночей'] = get_total_price(price, nights)
            i_hotel_dct['Сайт'] = ''.join(('https://hotels.com/ho', str(i_hotel['id'])))

            if data[4]:
                photo_lst = get_photos_from_rapidapi(i_hotel['id'], data[4])

                if photo_lst is str:
                    raise requests.exceptions.ConnectionError

                i_hotel_dct['photos'] = photo_lst
            hotel_dct[i_hotel['id']]: int = i_hotel_dct

        return hotel_dct

    except (requests.exceptions.ConnectionError, TypeError, KeyError, requests.exceptions.ConnectTimeout) as error:
        log.error('Ошибка с получением отелей', exc_info=error)
        return 'Технические неполадки с сайтом, попробуйте еще раз.'


def get_photos_from_rapidapi(hotel_id, num_photos) -> Union[List[types.InputMediaPhoto], str]:
    """
    Функция, которая для заданного отеля ищет на rapidapi заданное количество фотографий и
    возвращает список из types.InputMediaPhoto
    :param hotel_id: id отеля
    :param num_photos: количество фотографий
    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": str(hotel_id)}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config('x-rapidapi-key')
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring).json()
        size = 'b'
        photos_lst = list()
        for i_photo in range(int(num_photos)):
            url_photo = response['hotelImages'][i_photo]['baseUrl'].format(size=size)
            photo = types.InputMediaPhoto(url_photo)
            photos_lst.append(photo)

        return photos_lst

    except (requests.exceptions.ConnectionError, TypeError, KeyError, requests.exceptions.ReadTimeout) as error:
        log.error('Ошибка с получением фотографий', exc_info=error)
        return 'Ошибка'


def get_total_price(price: str, night: int) -> str:
    """
    Функция, которая из строки с ценой выделяет число, умножает на количество ночей,
    трансформирует в строку с валютой
    :param price: цена за ночь
    :param night: количество ночей
    """
    price_str = price.split(' ')[0]
    price = re.sub(r',', '.', price_str)
    total = round(float(price) * night, 3)
    total_str = re.sub(r'\.', ',', str(total))
    total_str = ' '.join((total_str, 'RUB'))
    return total_str


def get_distance(dist: str) -> str:
    """
    Функция, которая из строки с дистанцией выделяет число и переводит мили в киллометры
    :param dist: дистанция в милях
    """
    distance_str = dist.split(' ')[0]
    distance = re.sub(r',', '.', distance_str)
    distance_fl = round(float(distance) * 1.60934, 1)
    distance_str = ' '.join((str(distance_fl), 'км'))
    return distance_str
