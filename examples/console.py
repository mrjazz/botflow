import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from botflow.engine_console import ConsoleEngine
from examples.math_controller import MathController


ConsoleEngine(MathController()).run()
# ConsoleEngine(MathController).process("hello") # exec one command
