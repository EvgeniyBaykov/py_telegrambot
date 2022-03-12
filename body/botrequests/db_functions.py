import sqlite3
from typing import Tuple, Dict, Union, Optional, Any
from datetime import datetime
import logging

__all__ = ['create_tables', 'create_user', 'set_command', 'get_last_request_id',
           'set_city', 'get_last_request', 'set_id_city', 'set_check_in',
           'set_check_out', 'set_num_hotels', 'set_num_photos', 'get_request_lowprice',
           'set_request'
           ]

log = logging.getLogger(__name__)


def create_tables() -> None:
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
           min_distance TEXT,
           max_distance TEXT,
           min_price TEXT,
           max_price TEXT,
           num_hotels TEXT,
           photos TEXT,
           request TEXT);
        """)
        conn.commit()

    except sqlite3.DatabaseError as error:
        log.error('create_tables has not been successful', exc_info=error)
    finally:
        if conn:
            conn.close()


def create_user(user_id: int, first_name: str, last_name: str, username: str) -> None:
    """
    Функция, которая добавляет пользователя в таблицу "users", если его нет
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
    finally:
        if conn:
            conn.close()


def set_command(user_id: int, command: str) -> None:
    """
    Функция, которая добавляет команду запись в таблицу "history_requests",
    заполняет столбцы "user_id" и "command"
    :param user_id: id пользователя
    :param command: выбранная пользователем команда
    """

    try:
        cur_date = str(datetime.today())

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO history_requests (date_create, user_id, command) VALUES(?, ?, ?);",
                    (cur_date, user_id, command)
                    )
        conn.commit()
        conn.close()

    except sqlite3.DatabaseError as error:
        log.error('set_command has not been successful', exc_info=error)
    finally:
        if conn:
            conn.close()


def get_last_request_id(user_id: int) -> int:
    """
    Функция, которая передает id последнего запроса польщователя
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT request_id FROM history_requests WHERE user_id = ? "
                    "ORDER BY request_id DESC LIMIT 1;", (user_id,)
                    )
        id_request = cur.fetchone()[0]
        return id_request

    except sqlite3.DatabaseError as error:
        log.error('get_last_request_id has not been successful', exc_info=error)
    finally:
        if conn:
            conn.close()


def set_city(city: str, id_request) -> None:
    """
    Функция, которая добавляет город в таблицу "history_requests"
    :param city: город
    :param id_request: id запроса
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("UPDATE history_requests SET city = ? WHERE request_id = ?;", (city, id_request))
        conn.commit()
        conn.close()

    except sqlite3.DatabaseError as error:
        log.error('set_city has not been successful', exc_info=error)
    finally:
        if conn:
            conn.close()


def get_last_request(user_id: int) -> Tuple:  # Пытался вот так заполнить, но ничего не получилось Tuple[Optional[int, str]]
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
        result = cur.fetchone()
        return result

    except sqlite3.DatabaseError as error:
        log.error('get_last_request has not been successful', exc_info=error)
    finally:
        if conn:
            conn.close()


def set_id_city(id_city: str, request_id: int) -> None:
    """
    Функция, которая добавляет id искомого города в последний запрос таблицы "history_requests"
    :param id_city: id искомого города
    :param request_id: id последнего запроса пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("UPDATE history_requests SET id_city = ? WHERE request_id = ?;",
                    (id_city, request_id)
                    )
        conn.commit()
        conn.close()

    except sqlite3.DatabaseError as error:
        log.error('set_id_city has not been successful', exc_info=error)
    finally:
        if conn:
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
        conn.close()

    except sqlite3.DatabaseError as error:
        log.error('set_check_in has not been successful', exc_info=error)
    finally:
        if conn:
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
        conn.close()

    except sqlite3.DatabaseError as error:
        log.error('set_check_out has not been successful', exc_info=error)
    finally:
        if conn:
            conn.close()


def set_num_hotels(num_hotels: str, request_id: int) -> None:
    """
    Функция, которая добавляет количество отелей в последний запрос таблицы "history_requests"
    :param num_hotels: количество отелей
    :param request_id: id последнего запроса пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("UPDATE history_requests SET num_hotels = ? WHERE request_id = ?;",
                    (num_hotels, request_id)
                    )
        conn.commit()
        conn.close()

    except sqlite3.DatabaseError as error:
        log.error('set_num_hotels has not been successful', exc_info=error)
    finally:
        if conn:
            conn.close()


def set_num_photos(num_photos: str, request_id: int) -> None:
    """
    Функция, которая добавляет количество отелей в последний запрос таблицы "history_requests"
    :param num_photos: количество фотографий
    :param request_id: id последнего запроса пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("UPDATE history_requests SET photos = ? WHERE request_id = ?;",
                    (num_photos, request_id)
                    )
        conn.commit()
        conn.close()

    except sqlite3.DatabaseError as error:
        log.error('set_num_photos has not been successful', exc_info=error)
    finally:
        if conn:
            conn.close()


def get_request_lowprice(user_id: int) -> Tuple:
    """
    Функция, которая возвращает последний запрос пользователя.
    :param user_id: id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT id_city, check_in, check_out, num_hotels, photos FROM history_requests "
                    "WHERE user_id = ? ORDER BY request_id DESC LIMIT 1;", (user_id,)
                    )
        result = cur.fetchone()
        return result

    except sqlite3.DatabaseError as error:
        log.error('get_request_lowprice has not been successful', exc_info=error)
    finally:
        if conn:
            conn.close()


def create_request_str(req_dct: Dict[int, dict[Union[str, str]]]) -> str:
    """
    Функция, которая преобразует словарь полученного результата в строку
    :param req_dct: полученный результат
    """

    try:
        request_lst = list()
        for hotel in req_dct.values():
            msg_lst = [': '.join((k, str(v))) for k, v in hotel.items() if k != 'photos']
            msg = '\n'.join(msg_lst)
            request_lst.append(msg)
        request_str = '\n'.join(request_lst)
        return request_str

    except (ValueError, KeyError) as error:
        log.error('Проблема с полученным словарем', exc_info=error)


def set_request(req_dct: Dict[int, dict[Union[str, str]]], user_id: int) -> None:
    """
    Функция, которая добавляет полученный результат в последний запрос таблицы "history_requests"
    :param req_dct: полученный результат
    :param user_id: id пользователя
    """

    try:
        request_str = create_request_str(req_dct)
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        request_id = get_last_request_id(user_id)
        cur.execute("UPDATE history_requests SET request = ? WHERE request_id = ?;",
                    (request_str, request_id)
                    )
        conn.commit()
        conn.close()

    except sqlite3.DatabaseError as error:
        log.error('set_request has not been successful', exc_info=error)

    finally:
        if conn:
            conn.close()


def get_request(user_id: int) -> str:
    """
    Функция, возвращающая последний результат запроса польщователя
    :param user_id:id пользователя
    """

    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT request FROM history_requests "
                    "WHERE user_id = ? ORDER BY request_id DESC LIMIT 1;", (user_id,)
                    )
        result = cur.fetchone()
        return result

    except sqlite3.DatabaseError as error:
        log.error('get_request has not been successful', exc_info=error)
    finally:
        if conn:
            conn.close()
