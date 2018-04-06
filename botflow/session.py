from typing import Callable, Sequence, Dict
import logging
from botflow.response import Response

log = logging.getLogger(__name__)


class Session:

    def __init__(self):
        self.__handler = None
        self.__params = {}

    def process(self, commands: Dict[str, Callable], msg: str) -> Response:
        log.debug("request: %s" % msg)
        if self.__handler is not None:
            response = self.__handler(msg, self.__params)
            _, self.__handler, self.__params = response.extract()
        else:
            self.__handler = None
            self.__params = {}
            for command in commands:
                response = command.execute(msg)
                if response is not None:
                    _, self.__handler, self.__params = response.extract()
                    break
        if response is None:
            return Response("unknown command")
        return response


if __name__ == '__main__':
    pass
