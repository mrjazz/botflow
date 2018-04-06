from typing import Callable, Dict


class Response:

    def __init__(self, msg: str, handler: Callable = None):
        self.__msg = msg
        self.__handler = handler

    def msg(self) -> str:
        return self.__msg

    def handler(self) -> Callable:
        return self.__handler

    def extract(self):
        return self.__msg, self.__handler
