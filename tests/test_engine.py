from unittest import TestCase

from botflow.context import Context
from botflow.session import Session
from botflow.matchers import equals, regexp
from botflow.response import Response
from botflow.engine_telegram import TelegramEngine

from types import SimpleNamespace as Namespace
from unittest.mock import MagicMock

import logging
import json


logging.basicConfig(level=logging.DEBUG)


def do_test(msg, context):
    return Response("passed"), context


class EngineTestCase(TestCase):

    def test_messaging(self):
        engine = TelegramEngine()
        engine.add_command(equals("test"), do_test)
        request = json.loads('{"from_user": {"id": 1}, "text": "test"}', object_hook=lambda d: Namespace(**d))
        reply = MagicMock(return_value="passed")
        reply.method("passed")
        request.reply_text = reply
        self.assertEqual("test", request.text)
        response = engine._process_message(request)
        reply.assert_called_with("passed")
