import logging
from typing import Callable, Dict
from botflow.response import Response
from botflow.context import Context


log = logging.getLogger(__name__)


class Session:

    def __init__(self):
        self.__handler = None
        self.__context = Context()

    def process(self, commands: Dict[str, Callable], msg: str) -> Response:
        log.debug("request: %s" % msg)
        if self.__handler is not None:
            response, self.__context = self.__handler(msg, self.__context)
            _, self.__handler = response.extract()
            return response
        else:
            self.__handler = None
            for matcher, command in commands.items():
                if matcher(msg):
                    response, self.__context = command(msg, self.__context)
                    if response is not None:
                        _, self.__handler = response.extract()
                    return response
        return Response("unknown command")


if __name__ == '__main__':
    pass
