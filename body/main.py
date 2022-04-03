from datetime import date
import logging.config
import re
import time
from typing import Dict, List, Tuple, Optional, Union

from decouple import config
import telebot
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar

import botrequests
from settings import LOGGING_CONFIG, max_num_photos, max_num_hotels, id_sticker_time

logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger(__name__)

token_bot = config('telegram_bot_token')
bot = telebot.TeleBot(token_bot)


@bot.message_handler(commands=['hello_world', 'start'])
@bot.message_handler(func=lambda msg: msg.text.lower() == 'привет')
def send_welcome(message: types.Message) -> None:
    """Функция - приветствие. Отправляет пользователю описание команд Бота. """

    log.info('user_id: {user_id}'.format(user_id=message.from_user.id))
    msg: str = "Вас приветствует ТелеграмБот 'MyHotelBot'." \
               "\nЯ могу помочь Вам подобрать отель. Выберите команду:" \
               "\n/lowprice - поиск самых дешевых отелей в городе" \
               "\n/highprice - поиск самых дорогих отелей в городе" \
               "\n/bestdeal - поиск отелей, наиболее подходящих по цене и расположению от центра" \
               "\n/history - вывод истории поиска отелей" \
               "\n/restart - перезапуск поиска."
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=['restart'])
def restart(message):
    """
    Функция, которая отлавливает команду restart и переправляет пользователя
    в функцию send_welcome
    """
    log.info('Выполнен restart. user_id: {user_id}'.format(user_id=message.from_user.id))
    send_welcome(message)


@bot.message_handler(commands=['lowprice'])
def command_lowprice(message: types.Message) -> None:
    """
    Функция, которая выполняет команду "lowprice".
    Добавляет записи в БД: создание таблиц users и history_requests, в таблицу users добавляет нового пользователя,
    в таблицу "history_requests" создает новый запрос, заполняет [user_id, command].
    Переправляет в функцию 'get_cities'.
    В случае возникновения ошибки уведомляет пользователя и переправляет в функцию send_welcome.
    """

    log.info('Запрос. user_id: {user_id}'.format(user_id=message.from_user.id))

    result_table: Optional[str] = botrequests.create_tables()
    result_user: Optional[str] = botrequests.create_user(message.from_user.id, message.from_user.first_name,
                                                         message.from_user.last_name, message.from_user.username
                                                         )
    result_command: Optional[str] = botrequests.set_command(message.from_user.id, 'lowprice')
    if result_table or result_user or result_command:
        bot.send_message(message.from_user.id, 'Возникла неполадка c сервисом, попробуйте еще раз')
        send_welcome(message)
    else:
        msg: types.Message = bot.send_message(message.from_user.id, 'Выберите город:')
        bot.register_next_step_handler(msg, get_cities)

        log.info('Отработал успешно. user_id: {user_id}'.format(user_id=message.from_user.id))


@bot.message_handler(commands=['highprice'])
def command_highprice(message: types.Message) -> None:
    """
    Функция, которая выполняет команду "highprice".
    Добавляет записи в БД: создание таблиц users и history_requests, в таблицу users добавляет нового пользователя,
    в таблицу "history_requests" создает новый запрос, заполняет [user_id, command].
    Запрашивает искомы город и переправляет в функцию 'get_cities'.
    В случае возникновения ошибки уведомляет пользователя и переправляет в функцию send_welcome.
    """

    log.info('Запрос. user_id: {user_id}'.format(user_id=message.from_user.id))

    result_table: Optional[str] = botrequests.create_tables()
    result_user: Optional[str] = botrequests.create_user(message.from_user.id, message.from_user.first_name,
                                                         message.from_user.last_name, message.from_user.username
                                                         )
    result_command: Optional[str] = botrequests.set_command(message.from_user.id, 'highprice')
    if result_table or result_user or result_command:
        bot.send_message(message.from_user.id, 'Возникла неполадка c сервисом, попробуйте еще раз')
        send_welcome(message)
    else:
        msg: types.Message = bot.send_message(message.from_user.id, 'Выберите город:')
        bot.register_next_step_handler(msg, get_cities)

        log.info('Отработал успешно. user_id: {user_id}'.format(user_id=message.from_user.id))


@bot.message_handler(commands=['bestdeal'])
def command_bestdeal(message: types.Message) -> None:
    """
    Функция, которая выполняет команду "bestdeal".
    Добавляет записи в БД: создание таблиц users и history_requests, в таблицу users добавляет нового пользователя,
    в таблицу "history_requests" создает новый запрос, заполняет [user_id, command].
    Запрашивает у пользователя минимальную и максимальную цены за ночь и переправляет в функцию 'get_cities'.
    В случае возникновения ошибки уведомляет пользователя и переправляет в функцию send_welcome.
    """

    log.info('Запрос. user_id: {user_id}'.format(user_id=message.from_user.id))
    result_table: Optional[str] = botrequests.create_tables()
    result_user: Optional[str] = botrequests.create_user(message.from_user.id, message.from_user.first_name,
                                                         message.from_user.last_name, message.from_user.username
                                                         )
    result_command: Optional[str] = botrequests.set_command(message.from_user.id, 'bestdeal')
    if result_table or result_user or result_command:
        bot.send_message(message.from_user.id, 'Возникла неполадка c сервисом, попробуйте еще раз')
        send_welcome(message)
    else:
        msg: types.Message = bot.send_message(message.from_user.id,
                                              'Введите диапазон желаемых цен через пробел (пример: 1500 3000):'
                                              )
        bot.register_next_step_handler(msg, min_max_price)

        log.info('Отработал успешно. user_id: {user_id}'.format(user_id=message.from_user.id))


@bot.message_handler(commands=['history'])
def command_history(message: types.Message) -> None:
    """
    Функция, которая выполняет команду "history".
    Добавляет записи в БД: создание таблиц users и history_requests, в таблицу users добавляет нового пользователя.
    Переправляет в функцию 'show_history'.
    В случае возникновения ошибки уведомляет пользователя и переправляет в функцию send_welcome.
    """

    log.info('Запрос. user_id: {user_id}'.format(user_id=message.from_user.id))

    result_table: Optional[str] = botrequests.create_tables()
    result_user: Optional[str] = botrequests.create_user(message.from_user.id, message.from_user.first_name,
                                                         message.from_user.last_name, message.from_user.username
                                                         )

    if result_table or result_user:
        bot.send_message(message.from_user.id, 'Возникла неполадка c сервисом, попробуйте еще раз')
        send_welcome(message)
    else:
        show_history(message)


def min_max_price(message: types.Message) -> None:
    """
    Функция, которая в случае получения текста "/restart" переправляет в функцию send_welcome.
    Иначе
    Обрабатывает полученные минимальную и максимальную цены и, если они корректные, добавляет их в БД
    (history_requests [min_price, max_price]) и переправляет в функцию min_max_distance,
    в противном случае сообщает об это пользователю и предлагает еще раз ввести данные.
    В случае возникновения ошибки с БД переправляет в функцию command_bestdeal
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('Получено {answer}. user_id: {user_id}'.format(answer=message.text, user_id=message.from_user.id))

        result: Union[str, Tuple[int, int]] = botrequests.make_min_max_price(message)
        if result == 'Ошибка с БД':
            bot.send_message(message.from_user.id, 'Возникла неполадка c сервисом, попробуйте еще раз')
            command_bestdeal(message)
        elif result == 'Ошибка ввода':
            msg: types.Message = bot.send_message(message.from_user.id, 'Некорректный ввод, введите еще раз')
            bot.register_next_step_handler(msg, min_max_price)
        else:
            msg: types.Message = bot.send_message(message.from_user.id,
                                                  'Введите диапазон расстояния, на котором находится отель от центра '
                                                  'в км через пробел (пример: 2 5):'
                                                  )
            bot.register_next_step_handler(msg, min_max_distance)

            log.info('Отработал успешно. user_id: {user_id}'.format(user_id=message.from_user.id))


def min_max_distance(message: types.Message) -> None:
    """
    Функция, которая в случае получения текста "/restart" переправляет в функцию send_welcome.
    Иначе
    Обрабатывает полученные минимальную и максимальную дистанции, если они корректные, добавляет их в БД
    (history_requests [min_distance, max_distance]) и переправляет в функцию get_cities,
    в противном случае сообщает об это пользователю и предлагает еще раз ввести данные.
    В случае возникновения ошибки с БД переправляет в функцию command_bestdeal
    """

    if message.text == '/restart':
        restart(message)

    log.info('Получено {answer} user_id: {user_id}'.format(answer=message.text, user_id=message.from_user.id))

    result: Union[str, Tuple[int, int]] = botrequests.make_min_max_distance(message)
    if result == 'Ошибка с БД':
        bot.send_message(message.from_user.id, 'Возникла неполадка c сервисом, попробуйте еще раз')
        command_bestdeal(message)
    elif result == 'Ошибка ввода':
        msg: types.Message = bot.send_message(message.from_user.id, 'Некорректный ввод, введите еще раз')
        bot.register_next_step_handler(msg, min_max_distance)
    else:
        msg: types.Message = bot.send_message(message.from_user.id, 'Выберите город:')
        bot.register_next_step_handler(msg, get_cities)

        log.info('Отработал успешно. user_id: {user_id}'.format(user_id=message.from_user.id))


def get_cities(message: types.Message) -> None:
    """
    Функция, которая в случае получения текста "/restart" переправляет в функцию send_welcome.
    Иначе
    Получает список городов из функции get_cities_from_rapidapi и отправляет его в функцию selecting_city,
    Запрашивает у пользователя с помощью клавиатуры уточнение, какой именно город он ищет.
    Если ничего не найдено, сообщает пользователю и переправляет его в функцию get_cities.
    В случае возникновения ошибки с API переправляет в функцию command_bestdeal
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('Получено {answer}. user_id: {user_id}'.format(answer=message.text, user_id=message.from_user.id))

        cities_dct: Union[Dict[str, str], str] = botrequests.get_cities_from_rapidapi(message.text,
                                                                                      message.from_user.id
                                                                                      )
        if cities_dct == 'Error':
            bot.send_message(message.from_user.id, 'Технические неполадки с сайтом. Повторите запрос!')
            send_welcome(message)
        elif cities_dct == 'Null':
            msg: types.Message = bot.send_message(message.from_user.id, 'Ничего не найдено. Повторите запрос!')
            bot.register_next_step_handler(msg, get_cities)

        else:
            cities_lst = cities_dct.values()
            cities_markup: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                                                 resize_keyboard=True
                                                                                 )

            for i_city in cities_lst:
                cities_markup.add(types.KeyboardButton(i_city))
            msg: types.Message = bot.send_message(message.from_user.id, 'Уточните, пожалуйста:',
                                                  reply_markup=cities_markup
                                                  )
            bot.register_next_step_handler(msg, selecting_city)

            log.info('Отработал успешно. user_id: {user_id}'.format(user_id=message.from_user.id))


def selecting_city(message: types.Message) -> None:
    """
    Функция, которая в случае получения текста "/restart" переправляет в функцию send_welcome.
    Иначе
    Записывает id и название полученного города в БД (history_requests [id_city, city]).
    Запрашивается дату заезда при помощи клавиатуры - календарь.
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('Получено {answer} user_id: {user_id}'.format(answer=message.text, user_id=message.from_user.id))
        city: str = botrequests.get_city(message.from_user.id)
        pattern_city = r"'(\d+)': '([^']+)'"
        cities_lst: List[Tuple[str]] = re.findall(pattern_city, city)

        for i_city in cities_lst:
            if i_city[1] == message.text:
                botrequests.set_id_city(i_city[0], message.from_user.id)
                botrequests.set_city(i_city[1], message.from_user.id)
                break

        message_date: str = 'Выберите дату заезда'
        log.info('Отработал успешно. user_id: {user_id}'.format(user_id=message.from_user.id))
        calendar(message, message_date)


def calendar(message: types.Message, message_date: str) -> None:
    """Функция - клавиатура-календарь"""

    log.info('Начало работы. user_id: {user_id}'.format(user_id=message.from_user.id))
    calendar_markup, step = DetailedTelegramCalendar(one_time_keyboard=True, min_date=date.today(), locale='ru').build()
    bot.send_message(message.from_user.id,
                     message_date,
                     reply_markup=calendar_markup
                     )


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def callback_date(cal) -> None:
    """
    Функция, получает даты заезда и выезда, записывает их в БД (history_requests [check_in, check_out]).
    После полного выполнения переправляет в функцию 'number_hotels'.
    """

    result: Tuple[Optional[int, str]] = botrequests.get_last_request(cal.message.chat.id)
    request_id, check_in = result[0], result[2]

    if check_in:
        message_date: str = 'Выберите дату выезда'
        min_date_in_calendar: date = botrequests.next_day(check_in)
        answer, key, step = DetailedTelegramCalendar(min_date=min_date_in_calendar, locale='ru').process(cal.data)
    else:
        message_date: str = 'Выберите дату заезда'
        answer, key, step = DetailedTelegramCalendar(min_date=date.today(), locale='ru').process(cal.data)

    if not answer and key:
        bot.edit_message_text(message_date,
                              cal.message.chat.id,
                              cal.message.message_id,
                              reply_markup=key
                              )
    elif answer:
        if check_in:
            botrequests.set_check_out(answer, request_id)

            hotels_markup: types.ReplyKeyboardMarkup = botrequests.markup_hotels()
            msg: types.Message = bot.send_message(cal.message.chat.id,
                                                  'Выберите количество отелей (max={num}):'.format(num=max_num_hotels),
                                                  reply_markup=hotels_markup
                                                  )
            bot.register_next_step_handler(msg, number_hotels)

            log.info('Даты добавлены. user_id: {user_id}'.format(user_id=cal.message.chat.id))
        else:
            botrequests.set_check_in(answer, request_id)
            calendar(cal, 'Выберите дату выезда:')


def number_hotels(message: types.Message) -> None:
    """
    Функция, которая в случае получения текста "/restart" переправляет в функцию send_welcome.
    Иначе
    Проверяет полученное число отелей, если корректно, то добавляет в БД (history_requests [num_hotels]),
    спрашивает у пользователя, нужны ли фотографии и направляет в функцию 'ask_photos'.
    В случае некорректного ответа, переспрашивает о количестве отелей.
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('Получено {answer}. user_id: {user_id}'.format(answer=message.text, user_id=message.from_user.id))

        result: Optional[str] = botrequests.set_num_hotels(message.from_user.id, message.text)

        if result == 'ошибка в БД':
            bot.send_message(message.from_user.id, 'Технические неполадки с сервисом')
            hotels_markup: types.ReplyKeyboardMarkup = botrequests.markup_hotels()
            msg: types.Message = bot.send_message(message.from_user.id,
                                                  'Выберите количество отелей (max={num}):'.format(num=max_num_hotels),
                                                  reply_markup=hotels_markup
                                                  )
            bot.register_next_step_handler(msg, number_hotels)

        elif result == 'Неверный ввод':
            hotels_markup: types.ReplyKeyboardMarkup = botrequests.markup_hotels()
            msg: types.Message = bot.send_message(message.from_user.id,
                                                  'Введен некорректный ответ. \nВыберите количество отелей на '
                                                  'клавиатуре (max={num}):'.format(num=max_num_hotels),
                                                  reply_markup=hotels_markup
                                                  )
            bot.register_next_step_handler(msg, number_hotels)

        else:
            photo_markup: types.ReplyKeyboardMarkup = botrequests.markup_yes_no()
            msg: types.Message = bot.send_message(message.from_user.id, 'Нужны фотографии?', reply_markup=photo_markup)
            bot.register_next_step_handler(msg, ask_photos)

            log.info('Отработал успешно. user_id: {user_id}'.format(user_id=message.from_user.id))


def ask_photos(message: types.Message) -> None:
    """
    Функция, которая в случае получения текста "/restart" переправляет в функцию send_welcome.
    Иначе
    Если получен ответ "Нет" переправляет в функцию output.
    Если получен ответ "Да", то запрашивает у пользователя количество и направляет в функцию ask_num_photos.
    В случае некорректного ответа, переспрашивает о необходимости фотографий.
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('Получено {answer}. user_id: {user_id}'.format(answer=message.text, user_id=message.from_user.id))
        if message.text.lower() == 'нет':
            request_id: int = botrequests.get_last_request_id(message.from_user.id)
            output(message.from_user.id, request_id)

        elif message.text.lower() == 'да':
            photos_markup: types.ReplyKeyboardMarkup = botrequests.markup_photos()
            msg: types.Message = bot.send_message(message.from_user.id,
                                                  'Введите количество(max={num}):'.format(num=max_num_photos),
                                                  reply_markup=photos_markup
                                                  )
            bot.register_next_step_handler(msg, ask_num_photos)

        else:
            photo_markup: types.ReplyKeyboardMarkup = botrequests.markup_yes_no()
            msg: types.Message = bot.send_message(message.from_user.id,
                                                  'Введен некорректный ответ.\nВыберите ответ на клавиатуре:',
                                                  reply_markup=photo_markup
                                                  )
            bot.register_next_step_handler(msg, ask_photos)


def ask_num_photos(message: types.Message) -> None:
    """
    Функция, которая в случае получения текста "/restart" переправляет в функцию send_welcome.
    Иначе
    Проверяет количество фотографий, если корректно, то записывает в БД (history_requests [photos]) и
    переправляет в функцию output.
    В случае некорректного ответа, переспрашивает о количестве фотографий.
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('Получено {answer}. user_id: {user_id}'.format(answer=message.text, user_id=message.from_user.id))

        request_id: int = botrequests.get_last_request_id(message.from_user.id)
        result: Optional[str] = botrequests.set_num_photos(message.text, request_id)

        if result == 'ошибка в БД':
            bot.send_message(message.from_user.id, 'Технические неполадки с сервисом')
            photos_markup: types.ReplyKeyboardMarkup = botrequests.markup_photos()
            msg: types.Message = bot.send_message(message.from_user.id,
                                                  'Введите количество(max={num}):'.format(num=max_num_photos),
                                                  reply_markup=photos_markup
                                                  )
            bot.register_next_step_handler(msg, ask_num_photos)

        elif result == 'Неверный ввод':
            photos_markup: types.ReplyKeyboardMarkup = botrequests.markup_photos()
            msg: types.Message = bot.send_message(message.from_user.id,
                                                  'Введите количество(max={num}):'.format(num=max_num_photos),
                                                  reply_markup=photos_markup
                                                  )
            bot.register_next_step_handler(msg, ask_num_photos)

        else:
            output(message.from_user.id, request_id)


def output(user_id: int, request_id: int) -> None:
    """
    Функция, которая отправляет пользователю готовый ответ на запрос.
    В случае ошибки сообщает об этом пользователю и предлагает повторить запрос из истории
    """

    log.info('Начало работы. user_id: {user_id}'.format(user_id=user_id))

    bot.send_sticker(user_id, id_sticker_time)
    bot.send_message(user_id, 'Поиск займет несколько секунд, пожалуйста, подождите!')
    command: str = botrequests.get_command(request_id)

    if command == 'lowprice':
        hotels_dct: Union[Dict[int, dict[Union[str, str]]], str] = \
            botrequests.get_hotels_from_rapidapi_lowprice(user_id, request_id)
    elif command == 'highprice':
        hotels_dct: Union[Dict[int, dict[Union[str, str]]], str] = \
            botrequests.get_hotels_from_rapidapi_highprice(user_id, request_id)
    else:
        hotels_dct: Union[Dict[int, dict[Union[str, str]]], str] = \
            botrequests.get_hotels_from_rapidapi_bestdeal(user_id, request_id)

    if type(hotels_dct) is str:
        bot.send_message(user_id, hotels_dct)

    else:
        try:
            for hotel in hotels_dct.values():
                if hotel.get('photos'):
                    media_gr: List[types.InputMediaPhoto] = hotel['photos']
                    bot.send_media_group(user_id, media_gr, disable_notification=True)

                keyboard: types.InlineKeyboardMarkup = botrequests.markup_url(hotel['url'])
                msg_lst: List[str] = [': '.join((k, str(v))) for k, v in hotel.items() if k != 'photos' and k != 'url']
                msg: str = '\n'.join(msg_lst)
                bot.send_message(user_id, msg, reply_markup=keyboard)
                time.sleep(1)

            log.info('Запрос отправлен пользователю. user_id: {user_id}'.format(user_id=user_id))
        except Exception as err:
            log.error('Имя ошибки: {}'.format(err))
            bot.send_message(user_id, 'Неполадки с телеграмом')
            bot.send_message(user_id, 'Вы можете повторить свой запрос из истории')


def show_history(message: types.Message) -> None:
    """
    Функция, которая получает последние запросы пользователя. Если запросов не было, то сообщает об этом пользователю
    и переправляет в функцию send_welcome.
    Иначе отправляет пользователю клавиатуру с последними запросами
    """

    result: List[Tuple[Optional[int, str]]] = botrequests.get_user_request(message.from_user.id)
    if not result:
        log.info('Список запросов пуст. user_id: {user_id}'.format(user_id=message.from_user.id))
        bot.send_message(message.from_user.id, 'Вы еще не сделали ниодного запроса.\nДавайте это исправим!')
        send_welcome(message)

    else:
        for i_req in result:
            keyboard: types.InlineKeyboardMarkup = botrequests.markup_repeat_request(str(i_req[0]))
            output_text: str = botrequests.history_txt(i_req)
            bot.send_message(message.from_user.id, output_text, reply_markup=keyboard, disable_web_page_preview=True)

            log.info('отправил историю. user_id: {user_id}'.format(user_id=message.from_user.id))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery) -> None:
    """
    Функция получает в ответе пользователя id запроса и отправляет его в функцию output.
    Иначе предлагает пользователю нажать на необходимый запрос.
    """

    log.info('Id запрашиваемого запроса {answer} от пользователя {user_id}'.format(
            answer=call.data, user_id=call.message.chat.id)
            )
    if call.data:
        output(call.message.chat.id, int(call.data))
    else:
        bot.send_message(call.message.chat.id, 'Нажмите на интересующий вас запрос')


@bot.message_handler(content_types=['text'])
def bot_help(message: types.Message):
    if message.text.lower() != 'привет' or '/hello_world' or '/lowprice' or \
            '/highprice' or '/bestdeal' or '/history' or '/restart':
        msg: str = 'Чтобы начать поиск сайтов напишите "привет" или нажмите на команду /hello_world'
        bot.send_message(message.from_user.id, msg)


bot.infinity_polling()
