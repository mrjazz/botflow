from botflow.command.interface import Command
from botflow.response import Response


class CommandStr(Command):

    def __init__(self, pattern, fn):
        self.__pattern = pattern
        self.__fn = fn

    def execute(self, msg: str) -> Response:
        if msg == self.__pattern:
            return self.__fn(msg)
        return None

