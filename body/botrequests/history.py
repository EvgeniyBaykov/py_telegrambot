from telebot import types
import time
from datetime import date
import re
import logging

__all__ = ['f_date', 'num_nights', 'create_markup_hotels', 'create_markup_yes_no']

log = logging.getLogger(__name__)


def f_date(date_str: str) -> date:
    """
    Функция для конвертации даты в формат 'yyyy mm dd' типа datetime.date
    """
    date_str = ' '.join(date_str.split('-'))
    date_tpl = time.strptime(date_str, '%Y %m %d')
    my_date = date(date_tpl[0], date_tpl[1], date_tpl[2] + 1)
    return my_date


def num_nights(date_1: str, date_2: str) -> int:
    """
    Функция, которая создает заголовки для вывода отелей польщователю.
    :param date_1: дата заезда
    :param date_2: дата выезда
    """

    num_days = str(f_date(date_2) - f_date(date_1))
    pattern_days = r'\b\d+'
    nights = int(re.match(pattern_days, num_days)[0])
    return nights


def create_markup_hotels() -> types.ReplyKeyboardMarkup:
    """
    Функция, которая возвращает клавиатуру с кнопка 1 - 9
    """

    hotels_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    hotels_markup.add(types.KeyboardButton('1'), types.KeyboardButton('2'), types.KeyboardButton('3'))
    hotels_markup.add(types.KeyboardButton('4'), types.KeyboardButton('5'), types.KeyboardButton('6'))
    hotels_markup.add(types.KeyboardButton('7'), types.KeyboardButton('8'), types.KeyboardButton('9'))
    return hotels_markup


def create_markup_yes_no() -> types.ReplyKeyboardMarkup:
    """
    Функция, которая возвращает клавиатуру с кнопка 'Да', 'Нет'
    """

    answer_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    answer_markup.add(types.KeyboardButton('Да'), types.KeyboardButton('Нет'))
    return answer_markup
