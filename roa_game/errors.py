class GameIsNotExist(Exception):
    def __init__(self, message="Игра не началась"):
        self.msg = message
        super().__init__(self.msg)
