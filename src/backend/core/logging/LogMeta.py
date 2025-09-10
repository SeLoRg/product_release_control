import asyncio
from .log_decorator import log_method
from .logger import get_logger


class LogMeta(type):
    def __new__(mcs, name, bases, namespace):
        logger = get_logger(name=name)
        namespace["logger"] = logger

        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and asyncio.iscoroutinefunction(attr_value):
                namespace[attr_name] = log_method(logger=logger)(attr_value)
        return super().__new__(mcs, name, bases, namespace)
