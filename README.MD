#Telegram бот для поиска отелей

Данный бот предназначен для поиска отелей по всему миру по заданным 
параметрам в мессенджере Telegram.

## Как начать работу с ботом
Чтобы начать работу с ботом необходимо написать ему `привет`, 
ввести команду `/hello_world` , или `/start`.

##Команды бота
* `/hello_world` — приветствие и помощь по командам бота,
* `/lowprice` — вывод самых дешёвых отелей в городе,
* `/highprice` — вывод самых дорогих отелей в городе,
* `/bestdeal` — вывод отелей, наиболее подходящих по цене и расположению от
центра.
* `/history` — вывод истории поиска отелей

#Requirements
Python 3.9+

Для работы программы необходимо создать виртуальное окружение через модуль 
venv, который идёт в поставке Python 3.

Переименовать файл `.env.template` в `.env`. В этом файле необходимо присвоить 
соответствующим переменным токен telegram бота и ключ от API https://rapidapi.com/

Создать в директории `python_basic_diploma` директорию `log`

Установить пакеты командой `pip install -r requirements.txt`

###Внешние пакеты:
* [pyTelegramBotAPI](https://core.telegram.org/bots/api) - Telegram bot API
* [python-telegram-bot-calendar](https://github.com/artembakhanov/python-telegram-bot-calendar) Календарь
* [requests](https://docs.python-requests.org/en/latest/) - библиотека для парсинга сайтов
* [emoji](https://carpedm20.github.io/emoji/) - вставляем эмодзи в сообщения



>2022. by [Evgeniy Baykov](https://baykov1995@gmail.com)
