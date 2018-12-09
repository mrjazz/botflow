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
        @help this is quiz help
        """
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        self.__result = str(a + b)
        return ResponseMessage("%d+%d=?" % (a, b), response_action=self.validate)

    def test(self):
        # return ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True)
        return ResponseKeyboard("correct, one more time?", self.do_repeat)

    def items(self):
        button_list = [[InlineKeyboardButton("col%s" % i, callback_data="col%s" % i)] for i in range(10)]
        reply_markup = InlineKeyboardMarkup(button_list)
        buttons = ResponseButtons("message")
        buttons.set_markup(reply_markup)
        return buttons

    def col1(self):
        print("col1!")

    def do_repeat(self, params: str):
        if ResponseKeyboard.is_positive(params.lower()):
            return 'We are do it again!'
        else:
            return 'Sorry..'

    def do_exit(self):
        """
        @match exit
        @help terminate bot
        """
        logging.info("Terminating bot...")
        exit()
