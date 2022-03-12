import telebot
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date
import re
from decouple import config
import botrequests
import logging.config
from log.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger(__name__)

token_bot = config('telegram_bot_token')
bot = telebot.TeleBot(token_bot)


@bot.message_handler(commands=['hello_world'])
@bot.message_handler(func=lambda msg: msg.text.lower() == 'привет')
def send_welcome(message: types.Message) -> None:
    """Функция - приветствие. Отправляет пользователю описание команд Бота. """

    log.info('send_welcome - user_id: {user_id}'.format(user_id=message.from_user.id))
    msg = "Вас приветствует ТелеграмБот 'MyHotelBot'." \
          "\nЯ могу помочь Вам подобрать отель. Выберите команду:" \
          "\n/lowprice - поиск самых дешевых отелей в городе" \
          "\n/highprice - поиск самых дорогих отелей в городе" \
          "\n/bestdeal - поиск отелей, наиболее подходящих по цене и расположению от центра" \
          "\n/history - вывод истории поиска отелей" \
          "\n/restart - перезапуск поиска."
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=['restart'])
def restart(message):
    send_welcome(message)


@bot.message_handler(commands=['lowprice'])
def command_lowprice(message: types.Message) -> None:
    """
    Функция, которая выполняет команду "lowprice".
    Добавляет запись в БД, таблица "history_requests" (user_id, command).
    Переправляет в функцию 'get_cities'.
    """

    log.info('command_lowprice - user_id: {user_id}'.format(user_id=message.from_user.id))
    try:
        botrequests.create_tables()
        botrequests.create_user(message.from_user.id, message.from_user.first_name,
                                message.from_user.last_name, message.from_user.username
                                )
        botrequests.set_command(message.from_user.id, 'lowprice')

    except Exception:
        bot.send_message(message.from_user.id, "Возникла неполадка c сервисом, попробуйте еще раз")
        send_welcome(message)

    msg = bot.send_message(message.from_user.id, "Выберите город: ")
    bot.register_next_step_handler(msg, get_cities)


@bot.message_handler(commands=['highprice'])
def command_highprice(message: types.Message) -> None:
    """
    Функция, которая выполняет команду "highprice".
    Добавляет запись в БД, таблица "history_requests" (user_id, command).
    Переправляет в функцию 'get_cities'.
    """

    log.info('command_highprice - user_id: {user_id}'.format(user_id=message.from_user.id))
    try:
        botrequests.create_tables()
        botrequests.create_user(message.from_user.id, message.from_user.first_name,
                                message.from_user.last_name, message.from_user.username
                                )
        botrequests.set_command(message.from_user.id, 'highprice')

    except Exception:
        bot.send_message(message.from_user.id, "Возникла неполадка c сервисом, попробуйте еще раз")
        send_welcome(message)

    bot.send_message(message.from_user.id, "highprice в разработке")
    # msg = bot.send_message(message.from_user.id, "Выберите город: ")
    # bot.register_next_step_handler(msg, get_cities)


@bot.message_handler(commands=['bestdeal'])
def command_bestdeal(message: types.Message) -> None:
    """
    Функция, которая выполняет команду "bestdeal".
    Добавляет запись в БД, таблица "history_requests" (user_id, command).
    Переправляет в функцию 'get_cities'.
    """

    log.info('command_bestdeal - user_id: {user_id}'.format(user_id=message.from_user.id))
    try:
        botrequests.create_tables()
        botrequests.create_user(message.from_user.id, message.from_user.first_name,
                                message.from_user.last_name, message.from_user.username
                                )
        botrequests.set_command(message.from_user.id, 'bestdeal')

    except Exception:
        bot.send_message(message.from_user.id, "Возникла неполадка c сервисом, попробуйте еще раз")
        send_welcome(message)

    bot.send_message(message.from_user.id, "bestdeal в разработке")
    # msg = bot.send_message(message.from_user.id, "Выберите город: ")
    # bot.register_next_step_handler(msg, get_cities)


@bot.message_handler(commands=['history'])
def command_history(message: types.Message) -> None:
    """
    Функция, которая выполняет команду "history".
    """

    log.info('command_history - user_id: {user_id}'.format(user_id=message.from_user.id))
    try:
        botrequests.create_tables()
        botrequests.create_user(message.from_user.id, message.from_user.first_name,
                                message.from_user.last_name, message.from_user.username
                                )

    except Exception:
        bot.send_message(message.from_user.id, "Возникла неполадка c сервисом, попробуйте еще раз")
        send_welcome(message)

    bot.send_message(message.from_user.id, "История в разработке")


def get_cities(message: types.Message) -> None:
    """
    Функция, которая получает список городов из поиска (из функции "get_cities_from_rapidapi").
    Отправляет его в функцию "selecting_city",
    Запрашивает у пользователя с помощью клавиатуры уточнение, какой именно город он ищет.
    Переправляет в функцию 'selecting_city'.
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('get_cities - user_id: {user_id}'.format(user_id=message.from_user.id))

        cities_dct = botrequests.get_cities_from_rapidapi(message.text)
        if type(cities_dct) is str:
            bot.send_message(message.from_user.id, cities_dct)
            send_welcome(message)

        else:
            id_request = botrequests.get_last_request_id(message.from_user.id)
            botrequests.set_city(str(cities_dct)[1:-1], id_request)

            cities_lst = cities_dct.values()
            cities_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

            for i_city in cities_lst:
                cities_markup.add(types.KeyboardButton(i_city))
            msg = bot.send_message(message.from_user.id, 'Уточните, пожалуйста:', reply_markup=cities_markup)
            bot.register_next_step_handler(msg, selecting_city)


def selecting_city(message: types.Message) -> None:
    """
    Функция, в которой подтверждается город, записывает его id. Добавляет город в БД,
    таблица "history_requests" (request). Даты запрашиваются через календарь.
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('selecting_city - user_id: {user_id}'.format(user_id=message.from_user.id))
        result = botrequests.get_last_request(message.from_user.id)
        id_request, city, check_in = result

        pattern_city = r"'(\d+)': '([^']+)'"
        cities_lst = re.findall(pattern_city, city)

        for i_city in cities_lst:
            if i_city[1] == message.text:
                botrequests.set_id_city(i_city[0], id_request)
                botrequests.set_city(i_city[1], id_request)

        message_date = 'Выберите дату заезда'
        calendar(message, message_date)


def calendar(message: types.Message, message_date: str) -> None:
    """Функция - клавиатура-календарь"""

    log.info('calendar - user_id: {user_id}'.format(user_id=message.from_user.id))
    calendar_markup, step = DetailedTelegramCalendar(one_time_keyboard=True, min_date=date.today(), locale='ru').build()
    bot.send_message(message.from_user.id,
                     message_date,
                     reply_markup=calendar_markup)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def callback_date(cal) -> None:  # Не нахожу, что за тип у переменной
    """
    Функция, собирающая даты заезда и выезда через календарь.
    После полного выполнения переправляет в функцию 'number_hotels'.
    """

    result = botrequests.get_last_request(cal.message.chat.id)
    request_id, check_in = result[0], result[2]

    if check_in:
        message_date = 'Выберите дату выезда'
        min_date_in_calendar = botrequests.f_date(check_in)
        answer, key, step = DetailedTelegramCalendar(min_date=min_date_in_calendar, locale='ru').process(cal.data)
    else:
        message_date = 'Выберите дату заезда'
        answer, key, step = DetailedTelegramCalendar(min_date=date.today(), locale='ru').process(cal.data)

    if not answer and key:
        bot.edit_message_text(message_date,
                              cal.message.chat.id,
                              cal.message.message_id,
                              reply_markup=key)
    elif answer:
        if check_in:
            botrequests.set_check_out(answer, request_id)

            hotels_markup = botrequests.create_markup_hotels()
            msg = bot.send_message(cal.message.chat.id, 'Выберите количество отелей (max=9):',
                                   reply_markup=hotels_markup
                                   )
            bot.register_next_step_handler(msg, number_hotels)
        else:
            botrequests.set_check_in(answer, request_id)
            calendar(cal, 'Выберите дату выезда:')


def number_hotels(message: types.Message) -> None:
    """
    Функция которая добавляет количество отелей в БД, спрашивает у польщователя, нужны ли фотографии и
    направляет в функцию 'ask_photos'.
    В случае некорректного ответа, переспрашивает о количестве отелей.
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('number_hotels - user_id: {user_id}'.format(user_id=message.from_user.id))

        if 0 < int(message.text) < 10:
            request_id = botrequests.get_last_request_id(message.from_user.id)
            botrequests.set_num_hotels(message.text, request_id)

            photo_markup = botrequests.create_markup_yes_no()
            msg = bot.send_message(message.from_user.id, 'Нужны фотографии?', reply_markup=photo_markup)
            bot.register_next_step_handler(msg, ask_photos)

        else:
            hotels_markup = botrequests.create_markup_hotels()
            msg = bot.send_message(message.from_user.id, 'Введен некорректный ответ. '
                                                         '\nВыберите количество отелей на клавиатуре (max=9):',
                                   reply_markup=hotels_markup
                                   )
            bot.register_next_step_handler(msg, number_hotels)
            bot.register_next_step_handler(msg, ask_photos)


def ask_photos(message: types.Message) -> None:
    """
    Функция, которая переправляет в функцию 'ask_num_photos', если фотографии не нужны.
    Если фотографии, нужны, то спрашивает у польщователя сколько (max=10) и направляет в функцию 'ask_num_photos'.
    В случае некорректного ответа, переспрашивает о необходимости фотографий.
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('ask_photos - user_id: {user_id}'.format(user_id=message.from_user.id))

        if message.text.lower() == 'нет':
            lowprice_output(message)

        elif message.text.lower() == 'да':
            msg = bot.send_message(message.from_user.id, 'Введите количество(max=6):')
            bot.register_next_step_handler(msg, ask_num_photos)

        else:
            photo_markup = botrequests.create_markup_yes_no()
            msg = bot.send_message(message.from_user.id, 'Введен некорректный ответ. '
                                                         '\nВыберите ответ на клавиатуре:', reply_markup=photo_markup)
            bot.register_next_step_handler(msg, ask_photos)


def ask_num_photos(message: types.Message) -> None:
    """
    Функция, которая записывает в БД количество фотографий.
    В случае некорректного ответа, переспрашивает о количестве фотографий.
    """

    if message.text == '/restart':
        restart(message)

    else:
        log.info('ask_num_photos - user_id: {user_id}'.format(user_id=message.from_user.id))

        if 0 < int(message.text) < 7:
            request_id = botrequests.get_last_request_id(message.from_user.id)
            botrequests.set_num_photos(message.text, request_id)
            lowprice_output(message)
        else:
            photo_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            photo_markup.add(types.KeyboardButton('Да'), types.KeyboardButton('Нет'))
            msg = bot.send_message(message.from_user.id, 'Введён некорректный ответ.'
                                                         '\nХотите ввести количество фотографий ещё раз?',
                                   reply_markup=photo_markup
                                   )
            bot.register_next_step_handler(msg, ask_photos)


def lowprice_output(message: types.Message) -> None:
    """ Функция, которая отправляет пользователю готовый ответ на запрос. """

    log.info('lowprice_output - user_id: {user_id}'.format(user_id=message.from_user.id))

    bot.send_message(message.from_user.id, 'Поиск займет несколько секунд, пожалуйста, подождите!')
    result = botrequests.get_request_lowprice(message.from_user.id)
    hotels_dct = botrequests.get_hotels_from_rapidapi(result)
    if type(hotels_dct) is str:
        bot.send_message(message.from_user.id, hotels_dct)
        send_welcome(message)

    else:
        botrequests.set_request(hotels_dct, message.from_user.id)

        for hotel in hotels_dct.values():
            msg_lst = [': '.join((k, str(v))) for k, v in hotel.items() if k != 'photos']
            msg = '\n'.join(msg_lst)
            bot.send_message(message.from_user.id, msg)
            if result[4]:
                media_gr = hotel['photos']
                bot.send_media_group(message.from_user.id, media_gr)

        log.info('lowprice_output has been successful  - user_id: {user_id}'.format(user_id=message.from_user.id))


bot.infinity_polling()
