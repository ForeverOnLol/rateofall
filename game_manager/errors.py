class CantRunWithoutWords(Exception):
    def __init__(self, message="Слов нет. Запуск игры отменен, лобби расформировано."):
        self.msg = message
        super().__init__(self.msg)


class GameIsDone(Exception):
    def __init__(self, message="Игра завершена"):
        self.msg = message
        super().__init__(self.msg)
