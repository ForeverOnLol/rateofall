class EmptyParty(Exception):
    def __init__(self, message="Пустое лобби"):
        self.msg = message
        super().__init__(self.msg)


class TimerTimeOut(Exception):
    def __init__(self, message="Время таймера истекло"):
        self.msg = message
        super().__init__(self.msg)
        super().__init__(self.msg)


class TimerIsNotExist(Exception):
    def __init__(self, message="Таймер не существует"):
        self.msg = message
        super().__init__(self.msg)


class TimerStartError(Exception):
    def __init__(self, message="Невозможно запустить таймер"):
        self.msg = message
        super().__init__(self.msg)


class TimerAlreadyRun(Exception):
    def __init__(self, message="Таймер уже запущен"):
        self.msg = message
        super().__init__(self.msg)


class FillerAlreadyUsed(Exception):
    def __init__(self, message="Чат для ввода тем уже существует для данного лобби"):
        self.msg = message
        super().__init__(self.msg)


class FillerIsClosed(Exception):
    def __init__(self, message='Вы опоздали. Записать темы уже нельзя'):
        self.msg = message
        super().__init__(self.msg)


class MaxWordCount(Exception):
    def __init__(self, message='Превышен лимит тем.'):
        self.msg = message
        super().__init__(self.msg)


class GameIsRunning(Exception):
    def __init__(self, message="Игра уже запущена"):
        self.msg = message
        super().__init__(self.msg)


class WrongState(Exception):
    def __init__(self, message="Состояние игры не позволяет выполнить это действие"):
        self.msg = message
        super().__init__(self.msg)


class EmptyWords(Exception):
    def __init__(self, message="Слов нет. Возможно, потребуется заново создать лобби."):
        self.msg = message
        super().__init__(self.msg)


class CantStopWhileFiller(Exception):
    def __init__(self, message="Невозможно уничтожить лобби с игрой, пока таймер не истёк."):
        self.msg = message
        super().__init__(self.msg)
