from body.botrequests.history import num_nights
from body.botrequests.db_functions import set_city, get_request_low_high, set_request
import logging
import re
import requests
from settings import photo_size, headers_request
from telebot import types
from typing import Dict, List, Union

__all__ = ['get_cities_from_rapidapi', 'get_hotels_from_rapidapi_lowprice', 'get_photos_from_rapidapi_low',
           'get_total_price']

log = logging.getLogger(__name__)


def get_cities_from_rapidapi(city: str, user_id: int) -> Union[Dict[str, str], str]:
    """
    Функция, которая принимает строку и ищет на rapidapi все города с совпадением по строке.
    Возвращает словарь - id города: название.
    Если ничего не найдено, возвращает строку "Null".
    В случае ошибки с API возвращает строку "Error"
    :param city: искомый город
    :param user_id: id пользователя
    """

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    headers: Dict[str: str] = headers_request

    querystring_city = {"query": city, "locale": "ru_RU"}

    try:
        response = requests.request("GET", url, headers=headers, params=querystring_city, timeout=15).json()

        city_dct = dict()
        cities_lst: List[Dict[int: str]] = response['suggestions'][0]['entities']
        if not cities_lst:
            return 'Null'

        for i_city in cities_lst:
            if i_city['type'] == 'CITY':
                city: str = re.sub(r"<span class='highlighted'>", '', i_city['caption'])
                city: str = re.sub(r"</span>", '', city)
                city_dct[i_city["destinationId"]] = city

            set_city(str(city_dct)[1:-1], user_id)

        return city_dct

    except (requests.exceptions.ConnectionError,  requests.exceptions.ConnectTimeout, TypeError, KeyError,
            requests.exceptions.JSONDecodeError, requests.exceptions.ReadTimeout, IndexError) as error:
        log.error('Ошибка с получением города. user_id: {user_id}'.format(user_id=user_id), exc_info=error)

        return 'Error'


def get_hotels_from_rapidapi_lowprice(user_id: int, request_id: int) -> Union[Dict[int, dict[Union[str, str]]], str]:
    """
    Функция, которая по заданному запросу ищет отели на rapidapi.
    Добавляет полученный ответ в БД (history_requests [request]), если его не было. Возвращает словарь с данными отелей.
    Если ничего не найдено, возвращает строку "По вашему запросу ничего не найдено.".
    В случае ошибки с API возвращает строку "Технические неполадки с сайтом, попробуйте еще раз."
    :param user_id: id пользователя
    :param request_id: id запроса
    """

    url = "https://hotels4.p.rapidapi.com/properties/list"
    headers: Dict[str: str] = headers_request

    id_city, check_in, check_out, num_hotels, photos, request = get_request_low_high(request_id)

    querystring_hotel = {"destinationId": id_city, "checkIn": check_in, "checkOut": check_out,
                         "pageSize": num_hotels, "pageNumber": "1", "adults1": "1", "sortOrder": "PRICE",
                         "locale": "ru_RU", "currency": "RUB"
                         }

    hotel_dct = dict()
    try:
        response = requests.request("GET", url, headers=headers, params=querystring_hotel, timeout=15).json()
        log.info('user_id: {user_id}. Получен ответ: {res}.'.format(user_id=user_id, res=response))

        nights: int = num_nights(check_in, check_out)
        hotels_lst: List[Dict[int: Union[str, dict[str: str]]]] = response['data']['body']['searchResults']['results']
        if not hotels_lst:
            return 'По вашему запросу ничего не найдено.'

        for i_hotel in hotels_lst:
            i_hotel_dct = dict()
            price: str = i_hotel['ratePlan']['price']['current']

            i_hotel_dct['Название отеля']: str = i_hotel['name']
            try:
                i_hotel_dct['Адрес']: str = i_hotel['address']['streetAddress']
            except KeyError:
                i_hotel_dct['Адрес']: str = 'None'
            i_hotel_dct['Расстояние до центра']: str = i_hotel['landmarks'][0]['distance']
            i_hotel_dct['Цена за ночь']: str = price
            i_hotel_dct[f'Цена за {nights} ночей']: str = get_total_price(price, nights)
            i_hotel_dct['url']: str = ''.join(('https://hotels.com/ho', str(i_hotel['id'])))

            if photos:
                photo_lst: Union[List[types.InputMediaPhoto], str] = get_photos_from_rapidapi_low(i_hotel['id'], photos)
                if photo_lst is str:
                    raise requests.exceptions.ConnectionError

                i_hotel_dct['photos']: List[types.InputMediaPhoto] = photo_lst
            hotel_dct[i_hotel['id']]: int = i_hotel_dct

        if len(hotel_dct) == 0:
            return 'Ничего не найдено'

        if not request:
            set_request(user_id, hotel_dct)

        return hotel_dct

    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, TypeError, KeyError,
            requests.exceptions.JSONDecodeError, requests.exceptions.ReadTimeout) as error:
        log.error('Ошибка с получением отелей. user_id: {user_id}'.format(user_id=user_id), exc_info=error)

        return 'Технические неполадки с сайтом, попробуйте еще раз.'


def get_photos_from_rapidapi_low(hotel_id, num_photos) -> Union[List[types.InputMediaPhoto], str]:
    """
    Функция, которая для заданного отеля ищет на rapidapi заданное количество фотографий и
    возвращает список из types.InputMediaPhoto.
    В случае ошибки возвращает строку "Error".
    :param hotel_id: id отеля
    :param num_photos: количество фотографий
    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": str(hotel_id)}

    headers: Dict[str: str] = headers_request

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=15).json()
        size: str = photo_size
        photos_lst = list()
        for i_photo in range(int(num_photos)):
            url_photo: str = response['hotelImages'][i_photo]['baseUrl'].format(size=size)
            photo: types.InputMediaPhoto = types.InputMediaPhoto(url_photo)
            photos_lst.append(photo)

        return photos_lst

    except (requests.exceptions.ConnectionError, TypeError, KeyError, IndexError, requests.exceptions.ConnectTimeout,
            requests.exceptions.JSONDecodeError, requests.exceptions.ReadTimeout) as error:
        log.error('Ошибка с получением фотографий', exc_info=error)

        return 'Error'


def get_total_price(price: str, night: int) -> str:
    """
    Функция, которая из строки с ценой выделяет число, умножает на количество ночей,
    трансформирует в строку с валютой
    :param price: цена за ночь
    :param night: количество ночей
    """
    price_str: str = price.split(' ')[0]
    price: str = re.sub(r',', '.', price_str)
    total: float = round(float(price) * night, 3)
    total_str: str = re.sub(r'\.', ',', str(total))
    total_str: str = ' '.join((total_str, 'RUB'))

    return total_str
