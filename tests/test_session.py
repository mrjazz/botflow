from unittest import TestCase
from botflow.session import Session, Command, \
    ControllerExecutor, ResponseController, ResponseTerminateSession, ResponseMessage
from typing import Dict
import logging
import random


logging.basicConfig(level=logging.DEBUG)

MSG_HELLO = "Here is mach bot, use quiz command for quiz"


class MathController:

    def __init__(self):
        self.__result = 0

    def hello(self) -> str:
        return MSG_HELLO
    
    def quiz(self) -> ResponseMessage:                
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        self.__result = str(a + b)
        return ResponseMessage("%d+%d=?" % (a, b), response_action=self.check)
    
    def check(self, msg: str) -> str:        
        if msg == self.__result:
            return "correct"        
        return "incorrect"

    def test_params(self, params: tuple):
        """
        @regexp cmd(.*)
        @help test regular expressions
        """
        return params[0]


class Level2:

    def hello(self) -> str:
        return "Greetings on level2!"

    def stop(self) -> ResponseTerminateSession:
        return ResponseTerminateSession("Bye, Level2!")


class Level1:
    
    def hello(self):
        return "Greetings on level1!"
    
    def into(self) -> ResponseController:
        return ResponseController("ok", Level2())
    
    def stop(self) -> ResponseTerminateSession:
        return ResponseTerminateSession("Bye, Level1!")


class TestController:

    def test(self):
        """
        @match /test
        @help this is test command
        """
        return "ok"
    
    def regexp_command(self, msg: str):
        r"""
        @regexp \d+\+\d+
        @help mathematical expression
        """
        return "ok"
    
    def without_annotations(self, msg: str):
        pass


class WrongController:
    
    def with_wrong_annotations(self, msg: str):
        """
        @wrong annotation
        """
        pass


class SessionTestCase(TestCase):

    def test_command_with_wrong_annotation(self):        
        with self.assertRaises(Exception) as context:
            Command(WrongController(), "with_wrong_annotations")
        self.assertTrue("Unknown annotation wrong" in str(context.exception))

    def test_regexp_command(self):
        command = Command(TestController(), "regexp_command")
        self.assertEqual("mathematical expression", command.help())
        self.assertTrue(command.match("2+2"))
        self.assertTrue(command.match("21+21"))
        self.assertTrue(command.args()['msg'] is str)

    def test_command_without_annotation(self):
        command = Command(TestController(), "without_annotations")
        self.assertTrue(command.match("without_annotations"))
        self.assertFalse(command.match("wrong_command"))
        self.assertEqual(command.help(), Command.HELP_DEFAULT)

    def test_command_with_annotation(self):
        command = Command(TestController(), "test")
        self.assertTrue(command.match("/test"))
        self.assertFalse(command.match("test"))
        self.assertEqual(command.help(), "this is test command")

    def test_describe_commands(self):
        commands = ControllerExecutor(TestController()).commands()
        self.assertEqual(3, len(commands))

    def test_session(self):
        session = Session(TestController())

        # Test exec command
        self.assertEqual("ok", session.process("/test"))        
        self.assertEqual("Don't know what is 'unknown'", session.process("unknown"))

        # Test help functionality
        help = session.process("/help")
        self.assertRegex(help.msg(), "regexp_command - mathematical expression")
        self.assertRegex(help.msg(), "test - this is test command")
        self.assertRegex(help.msg(), "without_annotations - have no details about this command")

    def test_nested_sessions(self):
        session = Session(Level1())
        self.assertEqual("Greetings on level1!", session.process("hello"))
        self.assertEqual("Greetings on level2!", session.process("into"))        
        self.assertEqual("hello - have no details about this command\nstop - have no details about this command", 
            session.process("help"))
        self.assertEqual("Greetings on level1!", session.process("stop"))

    def test_responses(self):
        r1 = ResponseTerminateSession("ok")
        self.assertEqual("ok", r1)

        r2 = ResponseController("ok", TestController)
        self.assertEqual(TestController, r2.controller())

        r3 = ResponseMessage("ok", response_action="stop")
        self.assertEqual("ok", r3)
        self.assertEqual("stop", r3.response_action())

    def test_callback(self):
        session = Session(MathController())
        equation = session.process("quiz").msg()
        a = int(equation[0])
        b = int(equation[2])
        
        self.assertEqual("%d+%d=?" % (a, b), equation)    
        response = session.process(str(a+b))        
        self.assertEqual("correct", response)

        equation = session.process("quiz").msg()
        a = int(equation[0])
        b = int(equation[2])

        self.assertEqual("incorrect", session.process(str(a+b+1)))

    def test_match_params(self):
        command = Command(MathController(), "test_params")
        self.assertTrue(command.match("cmd 1"))
        self.assertEqual(1, len(command.match_params("cmd 1")))
        self.assertEqual(' 1', command.match_params("cmd 1")[0])

    def test_exec_params(self):
        session = Session(MathController())
        self.assertEqual(' 1', session.process("cmd 1"))
