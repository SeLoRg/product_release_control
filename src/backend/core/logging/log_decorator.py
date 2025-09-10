import functools
import logging


def log_method(logger: logging.Logger):
    """
    Декоратор для async методов, логирующий вызов и ошибки.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"Calling {func.__name__} args={args}, kwargs={kwargs}")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"{func.__name__} returned {result}")
                return result
            except Exception as e:
                logger.exception(f"Error in {func.__name__}: {e}")
                raise

        return wrapper

    return decorator
