class UserAlreadyInLobby(Exception):
    def __init__(self,
                 message='Пользователь уже находится в лобби. Возможно, вы уже '
                         'находитесь в лобби в другом чате. Попробуйте ввести '
                         'команду /stop в другом чате или доиграйте игру.'):
        self.msg = message
        super().__init__(self.msg)


class UserNotInLobby(Exception):
    def __init__(self,
                 message='Вас нет в лобби или игре, поэтому вы не можете задавать темы =('):
        self.msg = message
        super().__init__(self.msg)
