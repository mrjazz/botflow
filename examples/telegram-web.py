import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import logging
from typing import Dict

from botflow.engine_telegram import TelegramWebEngine, ResponseKeyboard, ResponseRemoveKeyboard
from examples.math_controller import MathController


logging.basicConfig(level=logging.INFO)


TOKEN = os.environ.get('TOKEN')
URL = os.environ.get('URL')
HOST = '0.0.0.0'
PORT = '5000'

engine = TelegramWebEngine(MathController())
engine.run(TOKEN, URL, HOST, PORT)
# engine.run(os.environ.get('TOKEN'), os.environ.get('URL'), os.environ.get('HOST'), os.environ.get('PORT'))