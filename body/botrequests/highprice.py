from telebot import types
import requests
from decouple import config
from typing import Dict, List, Union
import logging
from .history import num_nights
from .lowprice import get_total_price
from .db_functions import get_request_low_high, set_request
from settings import photo_size

__all__ = ['get_hotels_from_rapidapi_highprice']

log = logging.getLogger(__name__)


def get_hotels_from_rapidapi_highprice(user_id, request_id) -> Union[Dict[int, dict[Union[str, str]]], str]:
    """
    Функция, которая по заданному запросу ищет отели на rapidapi.
    Добавляет полученный ответ в БД (history_requests [request]), если его не было. Возвращает словарь с данными отелей.
    Если ничего не найдено, возвращает строку "По вашему запросу ничего не найдено.".
    В случае ошибки с API возвращает строку "Технические неполадки с сайтом, попробуйте еще раз."
    :param user_id: id пользователя
    :param request_id: id запроса
    """

    url = "https://hotels4.p.rapidapi.com/properties/list"
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config('x-rapidapi-key')
    }

    id_city, check_in, check_out, num_hotels, photos, request = get_request_low_high(request_id)

    querystring_hotel = {"destinationId": id_city, "checkIn": check_in, "checkOut": check_out,
                         "pageSize": num_hotels, "pageNumber": "1", "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST",
                         "locale": "ru_RU", "currency": "RUB"
                         }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring_hotel, timeout=15).json()
        log.info('user_id: {user_id}. Получен ответ: {res}.'.format(user_id=user_id, res=response))

        hotel_dct = dict()
        nights = num_nights(check_in, check_out)
        hotels_lst = response['data']['body']['searchResults']['results']
        if not hotels_lst:
            return 'По вашему запросу ничего не найдено.'

        for i_hotel in hotels_lst:
            i_hotel_dct = dict()
            price = i_hotel['ratePlan']['price']['current']

            i_hotel_dct['Название отеля'] = i_hotel['name']
            try:
                i_hotel_dct['Адрес'] = i_hotel['address']['streetAddress']
            except KeyError:
                i_hotel_dct['Адрес'] = 'None'
            i_hotel_dct['Расстояние до центра'] = i_hotel['landmarks'][0]['distance']
            i_hotel_dct['Цена за ночь'] = i_hotel['ratePlan']['price']['current']
            i_hotel_dct[f'Цена за {nights} ночей'] = get_total_price(price, nights)
            i_hotel_dct['url'] = ''.join(('https://hotels.com/ho', str(i_hotel['id'])))

            if photos:
                photo_lst = get_photos_from_rapidapi_high(i_hotel['id'], photos)

                if photo_lst is str:
                    raise requests.exceptions.ConnectionError

                i_hotel_dct['photos'] = photo_lst
            hotel_dct[i_hotel['id']]: int = i_hotel_dct

        if not request:
            set_request(user_id, hotel_dct, )

        return hotel_dct

    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, TypeError, KeyError,
            requests.exceptions.JSONDecodeError, requests.exceptions.ReadTimeout) as error:
        log.error('Ошибка с получением отелей. user_id: {user_id}'.format(user_id=user_id), exc_info=error)

        return 'Технические неполадки с сайтом, попробуйте еще раз.'


def get_photos_from_rapidapi_high(hotel_id, num_photos) -> Union[List[types.InputMediaPhoto], str]:
    """
    Функция, которая для заданного отеля ищет на rapidapi заданное количество фотографий и
    возвращает список из types.InputMediaPhoto.
    В случае ошибки возвращает строку "Error".
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
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=15).json()
        size = photo_size
        photos_lst = list()
        for i_photo in range(int(num_photos)):
            url_photo = response['hotelImages'][i_photo]['baseUrl'].format(size=size)
            photo = types.InputMediaPhoto(url_photo)
            photos_lst.append(photo)

        return photos_lst

    except (requests.exceptions.ConnectionError, TypeError, KeyError, IndexError, requests.exceptions.ReadTimeout,
            requests.exceptions.JSONDecodeError, requests.exceptions.ConnectTimeout) as error:
        log.error('Ошибка с получением фотографий', exc_info=error)

        return 'Error'
