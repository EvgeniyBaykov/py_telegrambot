import logging
import re
import sqlite3
from typing import Dict, List, Union

import requests
from telebot import types


from body.botrequests.db_functions import get_request_bestdeal, set_request
from body.botrequests.history import num_nights
from body.botrequests.lowprice import get_total_price
from settings import photo_size, headers_request

__all__ = ['get_hotels_from_rapidapi_bestdeal']

log = logging.getLogger(__name__)


def get_hotels_from_rapidapi_bestdeal(user_id: int, request_id: int) -> Union[Dict[int, dict[Union[str, str]]], str]:
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

    param_request = get_request_bestdeal(request_id)
    if type(param_request) is str:
        raise sqlite3.DatabaseError
    id_city, check_in, check_out, min_price, max_price, min_dist, max_dist, num_hotels, photos, request = param_request

    hotel_dct = dict()
    try:
        for i_page in range(1, 4):
            if len(hotel_dct) == int(num_hotels):
                break

            querystring_hotel = {"destinationId": id_city, "checkIn": check_in, "checkOut": check_out,
                                 "pageSize": '25', "priceMin": min_price, "priceMax": max_price,
                                 "pageNumber": str(i_page), "adults1": "1", "sortOrder": "PRICE",
                                 "locale": "ru_RU", "currency": "RUB"
                                 }

            response = requests.request("GET", url, headers=headers, params=querystring_hotel, timeout=15).json()
            log.info('user_id: {user_id}. Получен ответ: {res}.'.format(user_id=user_id, res=response))

            nights: int = num_nights(check_in, check_out)
            hotels_lst: List[Dict[int: Union[str, dict[str: str]]]] = \
                response['data']['body']['searchResults']['results']
            if not hotels_lst:
                return 'По вашему запросу ничего не найдено.'

            for i_hotel in hotels_lst:
                i_hotel_dct = dict()
                distance_str: str = i_hotel['landmarks'][0]['distance']
                distance: float = get_distance(distance_str)

                if float(min_dist) <= distance <= float(max_dist):
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
                        photo_lst: Union[List[types.InputMediaPhoto], str] = \
                            get_photos_from_rapidapi_bestdeal(i_hotel['id'], photos)
                        if photo_lst is str:
                            raise requests.exceptions.ConnectionError

                        i_hotel_dct['photos']: List[types.InputMediaPhoto] = photo_lst
                    hotel_dct[i_hotel['id']]: int = i_hotel_dct

                    if len(hotel_dct) == int(num_hotels):
                        break
        if len(hotel_dct) == 0:
            return 'Ничего не найдено'

        if not request:
            set_request(user_id, hotel_dct)

        return hotel_dct

    except (requests.exceptions.ConnectionError, TypeError, KeyError, requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout, requests.exceptions.JSONDecodeError) as error:
        log.error('Ошибка с получением отелей. user_id: {user_id}'.format(user_id=user_id), exc_info=error)

        return 'Технические неполадки с сайтом, попробуйте еще раз.'

    except sqlite3.DatabaseError as error:
        log.error('Ошибка с БД. user_id: {user_id}'.format(user_id=user_id), exc_info=error)
        return 'Техническая неполадка. Попробуйте еще раз!'


def get_photos_from_rapidapi_bestdeal(hotel_id, num_photos) -> Union[List[types.InputMediaPhoto], str]:
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

    except (requests.exceptions.ConnectionError, TypeError, KeyError, IndexError,
            requests.exceptions.ReadTimeout, requests.exceptions.JSONDecodeError) as error:
        log.error('Ошибка с получением фотографий', exc_info=error)

        return 'Error'


def get_distance(distance: str) -> float:
    """
    Функция, которая из строки с ценой выделяет число, умножает на количество ночей,
    трансформирует в строку с валютой
    :param distance: растояние до центра
    """

    distance_str: str = distance.split(' ')[0]
    distance_str: str = re.sub(r',', '.', distance_str)
    distance_fl: float = float(distance_str)

    return distance_fl
