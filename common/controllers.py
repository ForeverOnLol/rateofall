from abc import ABC
from common.models import Command
from common.views import CommandView


class Controller(ABC):
    def __init__(self, view, model):
        self.view = view
        self.model = model


class CommandController(Controller):
    def __init__(self, view: Command = CommandView(), model: Command = Command()):
        super().__init__(view, model)

    async def greeting(self, message):
        await self.view.greeting(message=message)

    async def start_in_private(self, message):
        await self.view.start_in_private(message=message)


