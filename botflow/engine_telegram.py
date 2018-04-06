#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram
import os
from telegram.error import NetworkError, Unauthorized
from telegram.ext import Updater, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from time import sleep
from typing import Callable, Dict
from botflow.session import Session
from botflow.response import Response
from botflow.engine import Engine

import logging


class TelegramEngine(Engine):

    def __init__(self):
        Engine.__init__(self)
        self.__session = {}
        self.__update_id = None

    def _process_message(self, message):
        print(message)
        logging.info("Q> %s" % message.text)

        user_id = message.from_user.id
        if self.__session.get(user_id) is None:
            self.__session.setdefault(user_id, Session())
        response = self.__session[user_id].process(self._commands, message.text)

        response_msg = response.msg()
        logging.info("A> %s" % response_msg)

        if isinstance(response, ResponseKeyboard):
            message.reply_text(response_msg, reply_markup=response.markup())
        else:
            message.reply_text(response_msg)

    def run(self, token):
        raise NotImplementedError


class TelegramSocketEngine(TelegramEngine):

    def run(self, token):
        bot = telegram.Bot(token)

        # get the first pending update_id, this is so we can skip over it in case
        # we get an "Unauthorized" exception.
        try:
            update_id = bot.get_updates()[0].update_id
        except IndexError:
            update_id = None

        while True:
            try:
                for update in bot.get_updates(offset=update_id, timeout=10):
                    update_id = update.update_id + 1
                    if update.message:
                        self._process_message(update.message)

            except NetworkError:
                sleep(1)
            except Unauthorized:
                update_id += 1


class TelegramWebEngine(TelegramEngine):

    def _error(bot, update, error):
        print('Update "%s" caused error "%s"', update, error)

    def run(self, token, url, port=5000):
        TOKEN = os.environ.get('TOKEN', token)
        PORT = int(os.environ.get('PORT', port))

        updater = Updater(TOKEN)
        dp = updater.dispatcher
        dp.add_handler(MessageHandler(Filters.all, lambda bot, update: self._process_message(update.message)))
        dp.add_error_handler(self._error)

        updater.bot.set_webhook(url + TOKEN)
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        updater.idle()


class ResponseRemoveKeyboard(Response):

    def markup(self):
        return ReplyKeyboardRemove()


class ResponseKeyboard(ResponseRemoveKeyboard):

    def isPositive(msg):
        return msg.lower() in ['yes', 'y']

    def markup(self):
        return ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True)


if __name__ == '__main__':
    pass