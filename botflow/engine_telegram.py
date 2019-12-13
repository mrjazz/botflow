#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from time import sleep

import telegram
from botflow.session import Session, Response
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.error import NetworkError, Unauthorized
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler


class TelegramMessage:

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        if isinstance(self._msg, Update) and self._msg.callback_query:
            return self._msg.callback_query.data
        return self._msg.message.text

    def get_user_id(self):
        if isinstance(self._msg, Update) and self._msg.callback_query:
            return self._msg.callback_query.from_user.id
        return self._msg.message.from_user.id

    def get_chat_id(self):
        if isinstance(self._msg, Update) and self._msg.callback_query:
            return self._msg.callback_query.message.chat.id
        return self._msg.message['chat']['id']

    def reply_text(self, *args, **kwargs):
        if isinstance(self._msg, Update):
            self._msg.effective_message.reply_text(*args, **kwargs)
        else:
            self._msg.message.reply_text(*args, **kwargs)

    def edit_text(self, *args, **kwargs):
        if isinstance(self._msg, Update):
            self._msg.effective_message.edit_text(*args, **kwargs)
        else:
            self._msg.message.edit_text(*args, **kwargs)

    def is_editable(self):
        if isinstance(self._msg, Update):
            return self._msg.callback_query is not None
        return False


class TelegramEngine:

    def __init__(self, controller):
        self.__session = {}
        self.__controller = controller
        self.__update_id = None
        self._sender = None
        self.before_process = None

    def _process_message(self, message: TelegramMessage):
        logging.info("Q> %s" % message)

        if self.before_process is not None:
            message = self.before_process(self, message)

        user_id = message.get_user_id()

        if self.__session.get(user_id) is None:
            fn_send = lambda msg: self.send_message(message.get_chat_id(), msg)
            self.__session.setdefault(user_id, Session(self.__controller, fn_send))

        response = self.__session[user_id].process(message, message.get_chat_id())

        response_msg = response.msg()
        logging.info("A> %s" % response_msg)

        if len(response_msg) > 4096:
            response_msg = '%s...' % response_msg[:1000]

        if isinstance(response, ResponseRemoveKeyboard):
            if isinstance(message, Update):
                self._sender(
                    message.callback_query.message.chat_id, response_msg,
                    reply_markup=response.markup(), parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                if isinstance(response, InlineResponseButtons) and message.is_editable():
                    message.edit_text(response_msg,
                                       reply_markup=response.markup(),
                                       parse_mode=telegram.ParseMode.MARKDOWN)
                else:
                    message.reply_text(response_msg,
                                       reply_markup=response.markup(),
                                       parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            if isinstance(message, Update):
                self.send_message(message.callback_query.message.chat_id, response_msg)
            elif isinstance(message._msg, Update) and message._msg.callback_query:  # TODO : rewrite this workaround
                self.send_message(message._msg.callback_query.message.chat_id, response_msg)
            else:
                message.reply_text(response_msg, parse_mode=telegram.ParseMode.MARKDOWN)

    def run(self, token):
        raise NotImplementedError

    def send_message(self, chat_id: int, msg: str):
        raise NotImplementedError


class TelegramSocketEngine(TelegramEngine):

    def run(self, token):
        bot = telegram.Bot(token)

        self._sender = bot.send_message

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

    def send_message(self, chat_id: int, msg: str):
        if self._sender is None:
            raise Exception("Sender doesn't exists")
        self._sender(chat_id, msg)


class TelegramWebEngine(TelegramEngine):

    @staticmethod
    def _error(bot, update, error):
        print('Update "%s" caused error "%s"' % (update, error))

    def run(self, token, url, host, port):
        updater = Updater(token)
        dp = updater.dispatcher
        dp.add_handler(MessageHandler(Filters.all, lambda bot, update: self._process_message(TelegramMessage(update))))
        dp.add_handler(CallbackQueryHandler(lambda bot, update: self._process_message(TelegramMessage(update))))

        dp.add_error_handler(self._error)

        self._sender = updater.bot.send_message

        # updater.bot.delete_webhook()
        # exit()

        updater.bot.set_webhook(url + '/' + token)
        updater.start_webhook(listen=host, port=int(port), url_path=token)

        updater.idle()

    def send_message(self, chat_id: int, msg: str):
        if self._sender is None:
            raise Exception("Sender doesn't exists")
        self._sender(chat_id, str(msg), parse_mode=telegram.ParseMode.MARKDOWN)


class ResponseRemoveKeyboard(Response):

    def markup(self):
        return ReplyKeyboardRemove()


class ResponseKeyboard(ResponseRemoveKeyboard):

    @staticmethod
    def is_positive(msg: str):
        return msg.lower() in ['yes', 'y']

    def markup(self):
        return ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True)


class ResponseButtons(ResponseRemoveKeyboard):

    def set_markup(self, markup):
        self.__markup = markup

    def markup(self):
        return self.__markup


class InlineResponseButtons(ResponseButtons):

    pass
