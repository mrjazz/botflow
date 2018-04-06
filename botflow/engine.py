from botflow.command.interface import Command


class Engine:

    def __init__(self):
        self._commands = []

    def add_command(self, command: Command):
        self._commands.append(command)
