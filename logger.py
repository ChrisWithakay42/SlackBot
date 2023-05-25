import logging
from functools import wraps


def log_to_file(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('log.txt')
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        logger.debug(f'Calling {func.__name__} with args: {args}, kwargs: {kwargs}')
        result = func(*args, **kwargs)
        logger.debug(f'{func.__name__} returned: {result}')

        logger.removeHandler(file_handler)
        file_handler.close()

        return result

    return wrapper
