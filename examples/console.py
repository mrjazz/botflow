import sys
sys.path.append("..")

from botflow.command.command_str import CommandStr
from botflow.response import Response
from botflow.engine_console import ConsoleEngine


def do_validate(msg: str, params):
    if params['result'] == msg:
        return Response("correct")
    else:
        return Response("incorrect")


def do_quiz(msg: str):
    return Response("2 + 2 = ?", do_validate, {"result": "4"})


def do_exit(msg: str):
    exit()


engine = ConsoleEngine()
engine.add_command(CommandStr("quiz", do_quiz))
engine.add_command(CommandStr("exit", do_exit))
engine.run()

