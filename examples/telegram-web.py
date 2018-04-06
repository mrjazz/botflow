import logging

from botflow.engine_telegram import TelegramWebEngine, ResponseKeyboard, ResponseRemoveKeyboard
from botflow.command.command_str import CommandStr


def do_validate(msg: str, params):
    if params['result'] == msg:
        return ResponseKeyboard("correct, one more time?", do_repeat)
    else:
        return ResponseKeyboard("incorrect, one more time?", do_repeat)


def do_repeat(msg: str, params):
    if ResponseKeyboard.isPositive(msg.lower()):
        return do_quiz('')
    else:
        return ResponseRemoveKeyboard('Bye!')


def do_quiz(msg: str):	
    return ResponseRemoveKeyboard("2 + 2 = ?", do_validate, {"result": "4"})


logging.basicConfig(level=logging.INFO)

engine = TelegramWebEngine()
engine.add_command(CommandStr("quiz", do_quiz))
engine.run("", "https://77d32070.ngrok.io/")
