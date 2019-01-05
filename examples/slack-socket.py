import os
from botflow.engine_slack import SlackSocketEngine
from examples.math_controller import MathController


engine = SlackSocketEngine(MathController())
engine.run(os.environ.get('SLACK_TOKEN'))
