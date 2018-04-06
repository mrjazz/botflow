import re
from botflow.command.interface import Command
from botflow.response import Response


class CommandRegexp(Command):

    def __init__(self, pattern, fn, params = re.MULTILINE | re.DOTALL | re.IGNORECASE):
        self.__pattern = re.compile(pattern, params)
        self.__fn = fn

    def execute(self, msg: str) -> Response:
        if self.__pattern.match(msg):
            return self.__fn(msg)
        return None
