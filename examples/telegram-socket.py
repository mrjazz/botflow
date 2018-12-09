import logging
import os

from botflow.engine_telegram import TelegramSocketEngine
from examples.math_controller import MathController

logging.basicConfig(level=logging.INFO)

engine = TelegramSocketEngine(MathController())
engine.run(os.environ.get('TOKEN'))
