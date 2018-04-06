from unittest import TestCase
from botflow.session import Session
from botflow.command.command_regexp import CommandRegexp
from botflow.command.command_str import CommandStr
from botflow.response import Response

import logging


logging.basicConfig(level=logging.DEBUG)


def do_validate(msg: str, params):
    if params['result'] == msg:
        return Response("correct")
    else:
        return Response("incorrect")


def do_quiz(msg: str):
    return Response("2 + 2 = ?", do_validate, {"result": "4"})


class ContextTestCase(TestCase):

    def test_quiz(self):
        session = Session()
        commands = [CommandStr("quiz", do_quiz)]
        self.assertEqual("2 + 2 = ?", session.process(commands, "quiz").msg())
        self.assertEqual("correct", session.process(commands, "4").msg())

        self.assertEqual("2 + 2 = ?", session.process(commands, "quiz").msg())
        self.assertEqual("incorrect", session.process(commands, "5").msg())

    def test_commands(self):
        self.assertEqual("passed", CommandRegexp("test\d", lambda x: "passed").execute("test1"))
        self.assertNotEqual("passed", CommandRegexp("test\d", lambda x: "passed").execute("testA"))
        self.assertEqual("passed", CommandStr("test", lambda x: "passed").execute("test"))

