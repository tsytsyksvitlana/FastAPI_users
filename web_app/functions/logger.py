from logging.config import dictConfig


def setup_logger():
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": (
                        "[%(asctime)s] %(levelname)s in %(name)s:%(lineno)d - "
                        "%(message)s"
                    ),
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": (
                        "%(asctime)s.%(msecs)03dZ %(levelname)s "
                        "%(name)s:%(lineno)d %(message)s"
                    ),
                },
            },
            "handlers": {
                "console": {
                    "class": "rich.logging.RichHandler",
                    "formatter": "console",
                    "level": "DEBUG",
                    "rich_tracebacks": True,
                    "markup": True,
                    "show_path": True,
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "file",
                    "level": "DEBUG",
                    "filename": "app.log",
                    "maxBytes": 1024 * 1024,
                    "backupCount": 3,
                    "encoding": "utf8",
                },
            },
            "loggers": {
                "app": {
                    "handlers": ["console", "rotating_file"],
                    "level": "DEBUG",
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["console", "rotating_file"],
                    "level": "DEBUG",
                    "propagate": False,
                },
            },
        }
    )
