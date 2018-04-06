from typing import Callable, Mapping
from botflow.session import Session
from botflow.engine import Engine


class ConsoleEngine(Engine):

    def __init__(self):
        Engine.__init__(self)
        self.__session = Session()

    def run(self):
        print("Welcome!")
        while True:
            print(self.__session.process(self._commands, input()).msg())


if __name__ == '__main__':
    pass