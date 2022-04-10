from datetime import datetime
import logging
from math import ceil
from typing import Tuple, Dict, List, Union, Optional

import sqlite3
from telebot import types

from body.botrequests.history import create_request_str
from settings import num_history_requests, max_num_hotels, max_num_photos

__all__ = ['create_tables',
           'create_user',
           'set_command',
           'get_command',
           'get_last_request_id',
           'set_city',
           'get_city',
           'get_last_request',
           'set_id_city',
           'set_check_in',
           'set_check_out',
           'set_num_hotels',
           'set_num_photos',
           'set_request',
           'set_min_price',
           'set_max_price',
           'make_min_max_price',
           'make_min_max_distance',
           'get_request_low_high',
           'get_request_bestdeal',
           'get_user_request'
           ]

log = logging.getLogger(__name__)


def create_tables() -> Optional[str]:
    """ Функция, которая создаём БД и 2 таблицы "users" и "history_requests" """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS users(
                    user_id INTEGER PRIMARY KEY, 
                    first_name TEXT, 
                    last_name TEXT, 
                    username TEXT
                    );
        """)
        conn.commit()

        cur.execute("""CREATE TABLE IF NOT EXISTS history_requests(
           request_id INTEGER PRIMARY KEY AUTOINCREMENT,
           date_create TEXT,
           user_id INTEGER,
           command TEXT,
           city TEXT,
           id_city TEXT,
           check_in TEXT,
           check_out TEXT,
           min_price TEXT,
           max_price TEXT,
           min_distance TEXT,
           max_distance TEXT,
           num_hotels TEXT,
           photos TEXT,
           request TEXT);
        """)
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('create_tables has not been successful', exc_info=error)
        return 'Ошибка в create_tables'
    finally:
        conn.close()


def create_user(user_id: int, first_name: str, last_name: str, username: str) -> Optional[str]:
    """
    Функция, которая добавляет пользователя в таблицу "users", если его нет.
    :param user_id: id пользователя
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param username: никнейм пользователя
    """
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?;", (user_id,))
        user_result = cur.fetchone()

        if not user_result:
            user = (user_id, first_name, last_name, username)
            cur.execute("INSERT INTO users VALUES(?, ?, ?, ?);", user)
            conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('create_user has not been successful', exc_info=error)
        return 'Ошибка в create_user'
    finally:
        conn.close()


def set_command(user_id: int, command: str) -> Optional[str]:
    """
    Функция, которая добавляет команду запись в таблицу "history_requests",
    заполняет столбцы "user_id" и "command"
    :param user_id: id пользователя
    :param command: выбранная пользователем команда
    """

    try:
        date = datetime.today()
        date_str = date.replace(microsecond=0)

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO history_requests (date_create, user_id, command) VALUES(?, ?, ?);",
                    (date_str, user_id, command)
                    )
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('set_command has not been successful', exc_info=error)
        return 'Ошибка в set_command'
    finally:
        conn.close()


def get_command(request_id: int) -> str:
    """
    Функция, которая передает команду, которую выбрал пользователь в заданном запросе.
    :param request_id: id запроса
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT command FROM history_requests WHERE request_id = ?;", (request_id,))
        command: str = cur.fetchone()[0]
        return command

    except sqlite3.DatabaseError as error:
        log.error('get_last_request_id has not been successful', exc_info=error)
    finally:
        conn.close()


def get_last_request_id(user_id: int) -> int:
    """
    Функция, которая передает id последнего запроса пользователя
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT request_id FROM history_requests WHERE user_id = ? "
                    "ORDER BY request_id DESC LIMIT 1;", (user_id,)
                    )
        req = cur.fetchone()
        id_request: int = req[0]
        return id_request

    except sqlite3.DatabaseError as error:
        log.error('get_last_request_id has not been successful', exc_info=error)
    finally:
        conn.close()


def set_city(city: str, user_id: int) -> None:
    """
    Функция, которая добавляет название гороа в таблицу "history_requests"
    :param city: город
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        id_request: int = get_last_request_id(user_id)
        cur.execute("UPDATE history_requests SET city = ? WHERE request_id = ?;", (city, id_request))
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('set_city has not been successful', exc_info=error)
    finally:
        conn.close()


def get_city(user_id: int) -> str:
    """
    Функция, которая передает название города, который выбрал пользователь в последнем запросе.
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT city FROM history_requests WHERE user_id = ? "
                    "ORDER BY request_id DESC LIMIT 1;", (user_id,)
                    )
        city: str = cur.fetchone()[0]
        return city

    except sqlite3.DatabaseError as error:
        log.error('get_city has not been successful', exc_info=error)
    finally:
        conn.close()


def get_last_request(user_id: int) -> Tuple[Union[int, str]]:
    """
    Функция, которая возвращает из последнего запроса пользователя значения "request_id", "city", "check_in"
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT request_id, city, check_in FROM history_requests "
                    "WHERE user_id = ? "
                    "ORDER BY request_id DESC LIMIT 1;", (user_id,)
                    )
        result: Tuple[Union[int, str]] = cur.fetchone()

        return result

    except sqlite3.DatabaseError as error:
        log.error('get_last_request has not been successful', exc_info=error)
    finally:
        conn.close()


def set_id_city(id_city: str, user_id: int) -> None:
    """
    Функция, которая добавляет id искомого города в последний запрос таблицы "history_requests"
    :param id_city: id искомого города
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        id_request: int = get_last_request_id(user_id)
        cur.execute("UPDATE history_requests SET id_city = ? WHERE request_id = ?;",
                    (id_city, id_request)
                    )
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('set_id_city has not been successful', exc_info=error)
    finally:
        conn.close()


def set_check_in(date: str, request_id: int) -> None:
    """
    Функция, которая добавляет дату заезда в последний запрос таблицы "history_requests"
    :param date: дату заезда
    :param request_id: id последнего запроса пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("UPDATE history_requests SET check_in = ? WHERE request_id = ?;",
                    (date, request_id)
                    )
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('set_check_in has not been successful', exc_info=error)
    finally:
        conn.close()


def set_check_out(date: str, request_id: int) -> None:
    """
    Функция, которая добавляет дату выезда в последний запрос таблицы "history_requests"
    :param date: дату заезда
    :param request_id: id последнего запроса пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("UPDATE history_requests SET check_out = ? WHERE request_id = ?;",
                    (date, request_id)
                    )
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('set_check_out has not been successful', exc_info=error)
    finally:
        conn.close()


def set_num_hotels(user_id: int, num_hotels: str) -> Optional[str]:
    """
    Функция, которая добавляет количество отелей в последний запрос таблицы "history_requests"
    :param user_id: id пользователя
    :param num_hotels: количество отелей
    """

    try:
        conn = sqlite3.connect('users.db')
        conn = sqlite3.connect('users.db')
        request_id: int = get_last_request_id(user_id)
        if 0 < int(num_hotels) < max_num_hotels + 1:
            cur = conn.cursor()
            cur.execute("UPDATE history_requests SET num_hotels = ? WHERE request_id = ?;",
                        (num_hotels, request_id)
                        )
            conn.commit()
        else:
            raise ValueError

    except sqlite3.DatabaseError as error:
        log.error('set_num_hotels has not been successful', exc_info=error)
        return 'ошибка в БД'
    except ValueError as error:
        log.error('Введена не цифра', exc_info=error)
        return 'Неверный ввод'
    finally:
        conn.close()


def set_num_photos(num_photos: str, request_id: int) -> Optional[str]:
    """
    Функция, которая добавляет количество фотографий в последний запрос таблицы "history_requests"
    :param num_photos: количество фотографий
    :param request_id: id последнего запроса пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        if 0 < int(num_photos) < max_num_photos + 1:
            cur.execute("UPDATE history_requests SET photos = ? WHERE request_id = ?;",
                        (num_photos, request_id)
                        )
            conn.commit()
        else:
            raise ValueError

    except sqlite3.DatabaseError as error:
        log.error('set_num_photos has not been successful', exc_info=error)
        return 'ошибка в БД'
    except ValueError as error:
        log.error('Введена не цифра', exc_info=error)
        return 'Неверный ввод'
    finally:
        conn.close()


def set_request(user_id: int, req_dct: Dict[int, dict[Union[str, str]]]) -> None:
    """
    Функция, которая добавляет полученный результат в последний запрос таблицы "history_requests"
    :param user_id: id пользователя
    :param req_dct: полученный результат
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        request_str: str = create_request_str(req_dct)
        request_id: int = get_last_request_id(user_id)
        cur.execute("UPDATE history_requests SET request = ? WHERE request_id = ?;",
                    (request_str, request_id)
                    )
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('set_request has not been successful', exc_info=error)

    finally:
        conn.close()


def get_request(user_id: int) -> str:
    """
    Функция, возвращающая последний результат запроса пользователя
    :param user_id:id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT request FROM history_requests "
                    "WHERE user_id = ? ORDER BY request_id DESC LIMIT 1;", (user_id,)
                    )
        result: str = cur.fetchone()
        return result

    except sqlite3.DatabaseError as error:
        log.error('get_request has not been successful', exc_info=error)
    finally:
        conn.close()


def make_min_max_price(message: types.Message) -> Union[str, Tuple[float, float]]:
    """
    Функция, которая принимает сообщение польователя, создает переменные min_price и max_price, добавляет их в БД.
    В случае ошибки с типом входных данных, возвращает строку 'Ошибка ввода'.
    В случае ошибки с записью в БД, возвращает строку  'Ошибка с БД'.
    :param message: сообщение от пользователя
    """
    try:
        min_price: int = ceil(float(message.text.split(' ')[0]))
        max_price: int = ceil(float(message.text.split(' ')[1]))
        if min_price < 0 or max_price < 0 or min_price > max_price:
            raise ValueError

        result_min_price = set_min_price(min_price, message.from_user.id)
        result_max_price = set_max_price(max_price, message.from_user.id)
        if result_min_price or result_max_price:
            return 'Ошибка с БД'

    except (ValueError, IndexError) as error:
        log.error('Неверный ввод диапазона цен', exc_info=error)
        return 'Ошибка ввода'

    else:
        return min_price, max_price


def set_min_price(min_price: int, user_id: int) -> Optional[bool]:
    """
    Функция, которая добавляет минимальную цену в таблицу "history_requests"
    :param min_price: минимальная цена
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        id_request: int = get_last_request_id(user_id)
        cur.execute("UPDATE history_requests SET min_price = ? WHERE request_id = ?;", (str(min_price), id_request))
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('set_city has not been successful', exc_info=error)
        return True
    finally:
        conn.close()


def set_max_price(max_price: int, user_id: int) -> Optional[bool]:
    """
    Функция, которая добавляет максимальную цену в таблицу "history_requests"
    :param max_price: минимальная цена
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        id_request: int = get_last_request_id(user_id)
        cur.execute("UPDATE history_requests SET max_price = ? WHERE request_id = ?;", (str(max_price), id_request))
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('set_city has not been successful', exc_info=error)
        return True
    finally:
        conn.close()


def make_min_max_distance(message: types.Message) -> Union[str, Tuple[float, float]]:
    """
    Функция, которая принимает сообщение польователя, создает переменные min_distance и max_distance, добавляет их в БД.
    В случае ошибки с типом входных данных, возвращает строку 'Ошибка ввода'.
    В случае ошибки с записью в БД, возвращает строку  'Ошибка с БД'.
    :param message: сообщение от пользователя
    """
    try:
        min_distance = float(message.text.split(' ')[0])
        max_distance = float(message.text.split(' ')[1])
        if min_distance < 0 or max_distance < 0 or min_distance > max_distance:
            raise ValueError

        result_min_distance = set_min_distance(min_distance, message.from_user.id)
        result_max_distance = set_max_distance(max_distance, message.from_user.id)
        if result_min_distance or result_max_distance:
            return 'Ошибка с БД'

    except (ValueError, IndexError) as error:
        log.error('Неверный ввод диапазона цен', exc_info=error)
        return 'Ошибка ввода'

    else:
        return min_distance, max_distance


def set_min_distance(min_distance: float, user_id: int) -> Optional[bool]:
    """
    Функция, которая добавляет минимальную дистанцию в таблицу "history_requests"
    :param min_distance: минимальная дистанция
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        id_request: int = get_last_request_id(user_id)
        cur.execute("UPDATE history_requests SET min_distance = ? WHERE request_id = ?;", (str(min_distance), id_request))
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('set_city has not been successful', exc_info=error)
        return True
    finally:
        conn.close()


def set_max_distance(max_distance: float, user_id: int) -> Optional[bool]:
    """
    Функция, которая добавляет максимальную дистанцию в таблицу "history_requests"
    :param max_distance: максимальная дистанция
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        id_request: int = get_last_request_id(user_id)
        cur.execute("UPDATE history_requests SET max_distance = ? WHERE request_id = ?;",
                    (str(max_distance), id_request)
                    )
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('set_city has not been successful', exc_info=error)
        return True
    finally:
        conn.close()


def get_request_low_high(request_id: int) -> Union[Tuple[Optional[str]], str]:
    """
    Функция, которая возвращает последний запрос пользователя для команд lowprice и highprice.
    :param request_id: id запроса
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT id_city, check_in, check_out, num_hotels, photos, request FROM history_requests "
                    "WHERE request_id = ?;", (request_id,)
                    )
        result = cur.fetchone()
        log.info(result)
        return result

    except sqlite3.DatabaseError as error:
        log.error('get_request_lowprice has not been successful', exc_info=error)
        return 'ошибка'
    finally:
        conn.close()


def get_request_bestdeal(request_id: int) -> Union[Tuple[Optional[str]], str]:
    """
    Функция, которая возвращает последний запрос пользователя для команды bestdeal.
    :param request_id: id запроса
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT id_city, check_in, check_out, min_price, max_price, "
                    "min_distance, max_distance, num_hotels, photos, request "
                    "FROM history_requests "
                    "WHERE request_id = ?;", (request_id,)
                    )
        result = cur.fetchone()
        return result

    except sqlite3.DatabaseError as error:
        log.error('get_request_bestdeal has not been successful', exc_info=error)
        return 'ошибка'
    finally:
        conn.close()


def get_user_request(user_id: int) -> List[Tuple[Union[int, str]]]:
    """
    Возвращает все запросы пользователя, у которых заполнен столбец history_requests [request] в обратном порядке
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM history_requests WHERE user_id = ? and request IS NOT NULL "
                    "ORDER BY request_id DESC;", (user_id,)
                    )
        result: List[Tuple[Union[int, str]]] = cur.fetchmany(num_history_requests)
        return result

    except sqlite3.DatabaseError as error:
        log.error('get_request_lowprice has not been successful', exc_info=error)
    finally:
        conn.close()
