from decouple import config


INFO_LOG_FILENAME = "../log/logfile.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s -- %(name)s -- %(funcName)s -- line: %(lineno)d -- %(levelname)s -- %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "logfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filename": INFO_LOG_FILENAME,
            "formatter": "default",
            "maxBytes": 2e20,
            "backupCount": 2,
            "encoding": "utf-8",
        },
    },
    "root": {"level": "INFO", "handlers": ["logfile"]},
}

headers_request = {'x-rapidapi-host': "hotels4.p.rapidapi.com",
                   'x-rapidapi-key': config('x-rapidapi-key')
                   }
num_history_requests = 3
max_num_hotels = 9
max_num_photos = 6
photo_size = 'b'
id_sticker_time = 'CAACAgIAAxkBAAEENoNiNi3VrQWj9ozdSRESxrPqyyopZQACBQEAAvcCyA_R5XS3RiWkoSME'
