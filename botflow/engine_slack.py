#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
from datetime import datetime

from slackclient import SlackClient

from botflow.session import Session, ResponseMessageWithBtns


class SlackSocketEngine:

    def __init__(self, controller, token):
        if token is None:
            raise Exception('Slack token is empty')

        self.__slack_client = SlackClient(token)
        self.__bot_id = self.__slack_client.api_call("auth.test")["user_id"]

        self.__session = {}
        self.__last_responses = {}
        self.__controller = controller
        self.__update_id = None
        self._sender = None
        self.before_process = None
        self.__seconds_between_commands = 10

    def get_bot_id(self) -> str:
        return self.__bot_id

    def process_message(self, message):
        if self.before_process is not None:
            message = self.before_process(self, message)

        if message is None:
            return  # nothing to processw

        logging.info(message)

        if 'event' in message:
            message = message['event']

        if 'subtype' in message:
            return

        if message['type'] == 'interactive_message':
            user_id = message['user']['id']
            channel_id = message['channel']['id']
        else:
            user_id = message['user']
            channel_id = message['channel']

        session_id = '%s-%s' % (channel_id, user_id)

        #  delay added because of heroku slow start
        if session_id in self.__last_responses.keys() \
                and (datetime.now() - self.__last_responses[session_id]).seconds < self.__seconds_between_commands:
            print("Too short delay between commands: %ssec" % (datetime.now() - self.__last_responses[session_id]))
            return

        if self.__session.get(session_id) is None:
            fn_send = lambda msg: self.send_message(channel_id, msg)
            self.__session.setdefault(session_id, Session(self.__controller, fn_send))

        if message['type'] in ['message', 'interactive_message', 'app_mention']:
            response = self.__session[session_id].process(SlackMessage(message))
        else:
            raise Exception("Unknown response type %s" % message)

        response_msg = response.msg()
        if len(response_msg) > 4096:
            response_msg = '%s...' % response_msg[:1000]

        if isinstance(response, ResponseMessageWithBtns):
            self.send_message(channel_id, response_msg, attachments=response.dump())
        else:
            self.send_message(channel_id, response_msg)

        self.__last_responses.setdefault(session_id, datetime.now())
        # self.send_message(message['user'], "You said %s" % message['text'])

    def send_message(self, chat_id: int, msg: str, attachments=None):
        logging.info("bot@%s> %s" % (chat_id, msg))
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
            while True:
                for event in self.__slack_client.rtm_read():
                    print(event)
                    if event["type"] == "message" and not "subtype" in event:
                        self._process_message(event)
                time.sleep(1)
        else:
            print("Connection failed. Exception traceback printed above.")


class SlackEngineClient:

    def __init__(self, token: str):
        if token is None:
            raise Exception('Slack token is empty')
        self.__slack_client = SlackClient(token)

    def send_message(self, chat_id: int, msg: str, attachments=None):
        logging.info("bot@%s> %s" % (chat_id, msg))
        if attachments is None:
            self.__slack_client.api_call(
                "chat.postMessage",
                channel=chat_id,
                text=msg
            )
        else:
            self.__slack_client.api_call(
                "chat.postMessage",
                channel=chat_id,
                text=msg,
                attachments=attachments
            )


class SlackMessage:

    def __init__(self, msg):
        self._msg = msg

    def get_user_id(self):
        return self._msg['user']['id'] if self._msg['type'] == 'interactive_message' else self._msg['user']

    def get_channel_id(self):
        return self._msg['channel']['id'] if self._msg['type'] == 'interactive_message' else self._msg['channel']

    def __str__(self):
        return self._msg['actions'][0]['value'] if self._msg['type'] == 'interactive_message' else self._msg['text']


if __name__ == "__main__":
    pass
