from logging.config import dictConfig


def setup_logger(env_mode: str):
    """
    Sets up logging configuration based on the environment mode.
    """
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "class": "logging.Formatter",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "[%(asctime)s] %(levelname)s in "
                "%(name)s:%(lineno)d - %(message)s",
            },
            "file": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "%(asctime)s.%(msecs)03dZ %(levelname)s "
                "%(name)s:%(lineno)d %(message)s",
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
            "sqlalchemy.engine": {
                "handlers": ["rotating_file"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console", "rotating_file"],
            "level": "DEBUG",
        },
    }

    if env_mode == "local":
        log_config["loggers"]["app"]["level"] = "INFO"
        log_config["loggers"]["uvicorn"]["level"] = "INFO"
        log_config["handlers"]["console"]["level"] = "INFO"
        log_config["handlers"]["rotating_file"]["level"] = "INFO"
    elif env_mode == "dev":
        log_config["loggers"]["app"]["level"] = "INFO"
        log_config["loggers"]["uvicorn"]["level"] = "INFO"
        log_config["loggers"]["sqlalchemy.engine"]["level"] = "WARNING"
        log_config["handlers"]["console"]["level"] = "INFO"
        log_config["handlers"]["rotating_file"]["level"] = "INFO"
    elif env_mode == "prod":
        log_config["loggers"]["app"]["level"] = "ERROR"
        log_config["loggers"]["uvicorn"]["level"] = "ERROR"
        log_config["loggers"]["sqlalchemy.engine"]["level"] = "ERROR"
        log_config["handlers"]["console"]["level"] = "ERROR"
        log_config["handlers"]["rotating_file"]["level"] = "ERROR"
        log_config["root"]["level"] = "ERROR"

    dictConfig(log_config)
