import datetime


# --- Кастомные ошибки ---
class UniqueCodeNotFoundError(Exception):
    pass


class UniqueCodeAlreadyUsedError(Exception):
    def __init__(self, aggregated_at: datetime.datetime):
        self.aggregated_at = aggregated_at


class UniqueCodeAttachedToAnotherBatchError(Exception):
    pass
