import sys

from botflow.context import Context

sys.path.append("..")

from botflow.matchers import equals
from botflow.response import Response
from botflow.engine_console import ConsoleEngine


def do_validate(msg: str, context: Context):
    if context.get('result') == msg:
        return Response("correct"), context
    else:
        return Response("incorrect"), context


def do_quiz(msg: str, context: Context):
    context.set("result", "4")
    return Response("2 + 2 = ?", do_validate), context


def do_exit(msg: str, context: Context):
    exit()


engine = ConsoleEngine()
engine.add_command(equals("quiz"), do_quiz)
engine.add_command(equals("exit"), do_exit)
engine.run()

