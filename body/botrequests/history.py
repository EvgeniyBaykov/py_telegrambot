from datetime import date, datetime, timedelta
import logging
import re
import time
from typing import Dict, List, Tuple, Union

import emoji
from telebot import types

__all__ = ['f_date',
           'num_nights',
           'markup_hotels',
           'markup_photos',
           'markup_yes_no',
           'markup_url',
           'next_day',
           'markup_repeat_request',
           'history_txt',
           'create_request_str']

log = logging.getLogger(__name__)


def f_date(date_str: str) -> date:
    """
    Функция для конвертации даты в формат 'yyyy mm dd' типа datetime.date
    :param date_str: дата
    """

    date_str: str = ' '.join(date_str.split('-'))
    date_tpl: time = time.strptime(date_str, '%Y %m %d')
    my_date: date = date(date_tpl[0], date_tpl[1], date_tpl[2])

    return my_date


def next_day(date_str: str) -> date:
    """
    Функция, которая получает дату и возвращает дату следующего дня
    :param date_str: дата
    """

    date_str: str = ' '.join(date_str.split('-'))
    date_tpl: datetime = datetime.strptime(date_str, '%Y %m %d')
    next_date_tpl: time = datetime.timetuple(date_tpl + timedelta(1))
    next_date: date = date(next_date_tpl[0], next_date_tpl[1], next_date_tpl[2])

    return next_date


def num_nights(date_1: str, date_2: str) -> int:
    """
    Функция, которая возвращает разницу между двумя датами в днях.
    :param date_1: дата заезда
    :param date_2: дата выезда
    """

    num_days: str = str(f_date(date_2) - f_date(date_1))
    pattern_days: str = r'\b\d+'
    nights: int = int(re.match(pattern_days, num_days)[0])

    return nights


def markup_hotels() -> types.ReplyKeyboardMarkup:
    """
    Функция, которая возвращает клавиатуру с кнопка 1 - 9
    """

    hotels_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                              resize_keyboard=True,
                                              input_field_placeholder='не более 9 отелей'
                                              )
    hotels_markup.row('1', '2', '3')
    hotels_markup.row('4', '5', '6')
    hotels_markup.row('7', '8', '9')

    return hotels_markup


def markup_photos() -> types.ReplyKeyboardMarkup:
    """
    Функция, которая возвращает клавиатуру с кнопка 1 - 6
    """

    hotels_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                              resize_keyboard=True,
                                              input_field_placeholder='не более 6 фотографий'
                                              )
    hotels_markup.row('1', '2', '3')
    hotels_markup.row('4', '5', '6')

    return hotels_markup


def markup_yes_no() -> types.ReplyKeyboardMarkup:
    """
    Функция, которая возвращает клавиатуру с кнопка 'Да', 'Нет'
    """

    answer_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    answer_markup.add(types.KeyboardButton('Да'), types.KeyboardButton('Нет'))

    return answer_markup


def markup_url(url: str) -> types.InlineKeyboardMarkup:
    """
    Функция, которая возвращает инлайновую кнопку "Перейти на сайт"
    """

    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Перейти на сайт" + emoji.emojize(':right_arrow:'), url=url)
    keyboard.add(url_button)

    return keyboard


def markup_repeat_request(id_req: str) -> types.InlineKeyboardMarkup:
    """
    Функция, которая возвращает инлайновую кнопку "Повторить запрос"
    """

    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Повторить запрос " + emoji.emojize(':repeat_button:'),
                                                 callback_data=id_req)
    keyboard.add(callback_button)
    log.info('создал клавиатуру')
    return keyboard


def history_txt(req: Tuple[str]) -> str:
    """
    Функция, которая создает текст для вывода пользователю истории.
    :param req: данные запроса польщователя
    """

    date_create, command, city, check_in, check_out, min_price, max_price, min_dist, max_dist = \
        req[1], req[3], req[4], req[6], req[7], req[8], req[9], req[10], req[11]

    if command == 'lowprice' or 'highprice':
        text = 'Дата запроса: {date_create}' \
               '\nКоманда: {command}' \
               '\nГород: {city}' \
               '\nДаты заезда/выезда: {check_in}/{check_out}'.format(date_create=date_create,
                                                                     command=command,
                                                                     city=city,
                                                                     check_in=check_in,
                                                                     check_out=check_out)
    else:
        text = 'Дата запроса: {date_create}' \
               '\nКоманда: {command}' \
               '\nГород: {city}' \
               '\nДаты заезда/выезда: {check_in}/{check_out}' \
               '\nДиапазон цен: {min_price} - {max_price}' \
               '\nДиапазон расстояний: {min_dist} - {max_dist} км'.format(date_create=date_create,
                                                                          command=command,
                                                                          city=city,
                                                                          check_in=check_in,
                                                                          check_out=check_out,
                                                                          min_price=min_price,
                                                                          max_price=max_price,
                                                                          min_dist=min_dist,
                                                                          max_dist=max_dist)

    return text


def create_request_str(req_dct: Dict[int, dict[Union[str, str]]]) -> str:
    """
    Функция, которая преобразует словарь полученного результата в строку
    :param req_dct: полученный результат
    """

    try:
        request_lst = list()
        for hotel in req_dct.values():
            msg_lst: List[str] = [': '.join((k, str(v))) for k, v in hotel.items() if k != 'photos']
            msg: str = '\n'.join(msg_lst)
            request_lst.append(msg)
        request_str: str = '\n'.join(request_lst)
        return request_str

    except (ValueError, KeyError) as error:
        log.error('Проблема с полученным словарем', exc_info=error)
