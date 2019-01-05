#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import json

from botflow.session import Session, ResponseMessageWithBtns
from slackclient import SlackClient


class SlackSocketEngine:

    def __init__(self, controller, token):
        self.__slack_client = SlackClient(token)
        # self.__slack_bot_id = None

        self.__session = {}
        self.__controller = controller
        self.__update_id = None
        self._sender = None
        self.before_process = None

    def process_message(self, message):
        logging.info(message)

        if self.before_process is not None:
            message = self.before_process(self, message)

        if 'event' in message:
            message = message['event']

        if 'subtype' in message:
            return

        if message['type'] == 'interactive_message':
            user_id = message['user']['id']
            channel_id = message['channel']['id']
            message_text = message['actions'][0]['value']
        else:
            user_id = message['user']
            channel_id = message['channel']
            message_text = message['text']

        if self.__session.get(user_id) is None:
            fn_send = lambda msg: self.send_message(channel_id, msg)
            self.__session.setdefault(user_id, Session(self.__controller, fn_send))

        if message['type'] in ['message', 'interactive_message']:
            response = self.__session[user_id].process(message_text)
        else:
            raise Exception("Unknown response type %s" % message)

        response_msg = response.msg()
        if len(response_msg) > 4096:
            response_msg = '%s...' % response_msg[:1000]

        if isinstance(response, ResponseMessageWithBtns):
            self.send_message(channel_id, response_msg, attachments=response.dump())
        else:
            self.send_message(channel_id, response_msg)
        # self.send_message(message['user'], "You said %s" % message['text'])

    def send_message(self, chat_id: int, msg: str, attachments=None):
        logging.info("bot> %s" % msg)
        if attachments is None:
            self.__slack_client.api_call(
                "chat.postMessage",
                channel=chat_id,
                text=msg
            )
        else:
            print(attachments)
            self.__slack_client.api_call(
                "chat.postMessage",
                channel=chat_id,
                text=msg,
                attachments=attachments
            )

    def run(self):
        if self.__slack_client.rtm_connect(with_team_state=False):
            print("Starter Bot connected and running!")
            # self.__slack_bot_id = self.__slack_client.api_call("auth.test")["user_id"]
            while True:
                for event in self.__slack_client.rtm_read():
                    print(event)
                    if event["type"] == "message" and not "subtype" in event:
                        self._process_message(event)
                time.sleep(1)
        else:
            print("Connection failed. Exception traceback printed above.")

