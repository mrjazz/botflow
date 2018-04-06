from unittest import TestCase

from botflow.context import Context
from botflow.session import Session
from botflow.matchers import equals, regexp
from botflow.response import Response

import logging


logging.basicConfig(level=logging.DEBUG)


def do_validate(msg: str, context: Context):
    if context.get('result') == msg:
        return Response("correct"), context
    else:
        return Response("incorrect"), context


def do_quiz(msg: str, context):
    context.set('result', "4")
    return Response("2 + 2 = ?", do_validate), context


class ContextTestCase(TestCase):

    def test_quiz(self):
        session = Session()
        commands = {equals("quiz"): do_quiz}
        self.assertEqual("2 + 2 = ?", session.process(commands, "quiz").msg())
        self.assertEqual("correct", session.process(commands, "4").msg())

        self.assertEqual("2 + 2 = ?", session.process(commands, "quiz").msg())
        self.assertEqual("incorrect", session.process(commands, "5").msg())

    def test_commands(self):
        self.assertTrue(equals("test")("test"))
        self.assertTrue(regexp("test\d")("test1"))
        self.assertFalse(regexp("test\d")("testA"))

