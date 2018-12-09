import logging

import time
import random

from typing import Dict

from botflow.engine_telegram import ResponseKeyboard, ResponseButtons
from botflow.session import ResponseMessage, ResponseAsync
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


class MathController:

    def __init__(self):
        self.__result = 0
    
    def hello(self):
        """
        @help greetings command
        """
        return "Hi!"
    
    def delay(self):
        return ResponseAsync("Started...", lambda: time.sleep(3), done_action=lambda: "Done!")
    
    def validate(self, msg: str):
        if not msg.isdigit():
            return None
        if msg == self.__result:
            response = "correct"
        else:
            response = "incorrect"
        return ResponseAsync(response, lambda: time.sleep(1), done_action=self.quiz)
    
    def quiz(self):
        """
        @help quiz command
        """
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        self.__result = str(a + b)
        return ResponseMessage("%d+%d=?" % (a, b), response_action=self.validate)

    def do_repeat(self, params: str):
        if ResponseKeyboard.is_positive(params.lower()):
            return 'We are do it again!'
        else:
            return 'Sorry..'

    def terminate(self):
        """
        @match exit
        @help terminate bot (will work as `exit`)
        """
        logging.info("Terminating bot...")
        exit()
