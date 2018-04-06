from typing import Callable, Dict


class Response:

    def __init__(self, msg: str, handler: Callable = None, params: Dict = {}):
        self.__msg = msg
        self.__handler = handler
        self.__params = params

    def msg(self) -> str:
        return self.__msg

    def handler(self) -> Callable:
        return self.__handler

    def params(self) -> Dict:
        return self.__params

    def extract(self):
        return self.__msg, self.__handler, self.__params
