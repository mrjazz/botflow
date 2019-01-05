from flask import Flask, request, make_response, Response
import os
import logging
import json

from slackclient import SlackClient

from botflow.engine_slack import SlackSocketEngine
from examples.math_controller import MathController

SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
slack_bot = SlackSocketEngine(MathController(), SLACK_BOT_TOKEN)

app = Flask(__name__)


@app.route("/", methods=["POST"])
def message_actions():
    # registration
    try:
        req = request.json
        print(req)

        if req is not None and 'challenge' in req:
            return make_response(request.json['challenge'], 200)

        if request.form is not None and 'payload' in request.form:
            # handle action
            slack_bot.process_message(json.loads(request.form['payload']))
        elif 'event' in req:
            # standard message
            slack_bot.process_message(req)
        else:
            raise Exception('Unknown message %s' % request)

        # if 'actions' in req:
        #     # req["actions"][0]["value"]
        #     # req["channel"]["id"]
        #     pass
        # elif 'event' in req:
        #     # req['event']['channel']
        #     # req['event']['text']
        #     pass

        return make_response("", 200)
    except Exception as e:
        logging.exception(e)
        return make_response(str(e), 500)



@app.route('/', methods=['GET'])
def home():
    return Response('It works!')


# Send a Slack message on load. This needs to be _before_ the Flask server is started

# A Dictionary of message attachment options
attachments_json = [
    {
        "fallback": "Upgrade your Slack client to use messages like these.",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "callback_id": "menu_options_2319",
        "actions": [
            {
                "name": "bev_list",
                "text": "One",
                "value": "One",
                "type": "button"
            },
            {
                "name": "bev_list",
                "text": "Two",
                "value": "Two",
                "type": "button"
            }
        ]
    }
]

# Send a message with the above attachment, asking the user if they want coffee
# slack_client.api_call(
#     "chat.postMessage",
#     channel="#onixbot-test",
#     text="Would you like some coffee? :coffee:",
#     attachments=attachments_json
# )

if __name__ == "__main__":
    app.run()