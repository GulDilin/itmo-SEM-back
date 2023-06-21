import logging

LOG_NAME = 'backend'
LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(asctime)s | %(levelname)s | %(name)s - %(process)s - %(threadName)s - %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"  # noqa
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
formatter = logging.Formatter(LOG_FORMAT)


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/health") == -1


logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


def get_logger(name: str = "fast_api") -> logging.Logger:
    return logging.getLogger(name)


logger = get_logger()
