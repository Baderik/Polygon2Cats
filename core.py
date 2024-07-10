import logging

__all__ = ["Logged", "logged"]


def logged(cls):
    cls.logger = logging.getLogger(cls.__name__)
    return cls


class classproperty:
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class Logged:
    _logger = None

    @classproperty
    def logger(cls):
        if cls._logger is None:
            cls._logger = logging.getLogger(cls.__name__)
        return cls._logger
