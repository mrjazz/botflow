from typing import Callable


class Engine:

    def __init__(self):
        self._commands = {}

    def add_command(self, matcher: Callable, action: Callable):
        self._commands.setdefault(matcher, action)


if __name__ == '__main__':
    pass