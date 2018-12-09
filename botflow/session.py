import io
import logging
import re
from contextlib import redirect_stdout
from threading import Thread
from typing import Dict, Callable

import botflow.matches as matches
from telegram import ReplyMarkup

log = logging.getLogger(__name__)


class Response:
    def __init__(self, msg: str, response_action: Callable=None):
        self.__msg = msg
        self.__response_action = response_action

    def response_action(self) -> str:
        return self.__response_action

    def msg(self) -> str:
        return self.__msg

    def __repr__(self):
        return self.msg()

    def __eq__(self, other):
        return other == self.msg()


class ResponseTerminateSession(Response):
    pass


class ResponseAsync(Response):

    def __init__(self, msg: str, task: Callable, response_action: Callable=None, done_action: Callable = None):
        super().__init__(msg, response_action=response_action)
        self.__task = task        
        self.__done_action = done_action

    def run_task(self) -> str:
        log.info("Start task: '%s'" % self.__task)        
        if self.__task is None:
            raise Exception("Task is not defined but executed")
        self.__task()
        if self.__done_action is not None:
            return self.__done_action()


class ResponseController(Response):

    def __init__(self, msg, controller, response_action: Callable=None):
        super().__init__(msg, response_action=response_action)
        self.__controller = controller

    def controller(self):
        return self.__controller


class ResponseMessage(Response):
    pass


class Command:

    HELP_DEFAULT = ""

    def __init__(self, controller: object, method: str):        
        command = getattr(controller, method)

        self.__controller = controller
        self.__command = command
        self.__matcher = matches.equals(command.__name__)
        self.__name = command.__name__
        self.__args = command.__annotations__
        self.__help = self.HELP_DEFAULT
        self.__regexp = ''

        metadata = command.__doc__
        if metadata is not None:
            p = re.compile(r"@(.*?)\s+(.*)", re.IGNORECASE)
            for line in metadata.split("\n"):
                res = p.match(line.strip())
                if res:
                    if res.groups(0)[0] == 'match':
                        self.__matcher = matches.equals(res.groups(0)[1])
                    elif res.groups(0)[0] == 'regexp':
                        self.__matcher = matches.regexp(res.groups(0)[1])
                        self.__regexp = res.groups(0)[1]
                    elif res.groups(0)[0] == 'help':
                        self.__help = res.groups(0)[1].strip()
                    else:
                        raise Exception("Unknown annotation %s" % res.groups(0)[0])

    def match(self, msg: str) -> bool:
        return self.__matcher(msg)

    def match_params(self, msg: str) -> bool:
        p = re.compile(self.__regexp, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        return p.match(msg).groups()

    def args(self) -> Dict:
        return self.__args

    def help(self) -> str:
        return self.__help

    def name(self) -> str:
        return self.__name

    def execute(self, args: Dict) -> Response:
        f = io.StringIO()
        with redirect_stdout(f):
            result = self.__command(**args)
        if result is None:
            return f.getvalue()
        else:
            return result


class ControllerExecutor:

    def __init__(self, controller):        
        self.__controller = controller
        self.__commands = []
        for method in dir(controller):
            if method[:1] != '_':
                self.__commands.append(Command(controller, method))
        
    def __get_command(self, msg: str) -> Command:        
        for command in self.__commands:
            if command.match(msg):
                return command
        return None

    def commands(self):
        return self.__commands

    def execute(self, msg: str):
        command = self.__get_command(msg)
        if command is None:
            return None  # command is not found

        command_args = command.args()
        args = {}
        for arg, arg_type in command_args.items():

            # TODO : make sense do this validation on commands initialization
            # if arg in ['state', 'context']:
            #     if arg_type is not Dict:
            #         raise Exception('Wrong arg_type for arg %s in %s' % (arg, command.name()))
            #     args.setdefault(arg, self.__state)

            if arg == 'msg':
                if arg_type is not str:
                    raise Exception('Wrong arg_type for arg %s in %s' % (arg, command.name()))
                args.setdefault(arg, msg)
            elif arg == 'params':
                args.setdefault(arg, command.match_params(msg))
            elif arg == 'return':
                if arg_type not in [str, Response, ResponseTerminateSession, ResponseController, ResponseMessage]:
                    raise Exception('Wrong return type "%s" in %s' % (arg_type, command.name()))
            else:
                raise Exception('Unknown arg %s in %s' % (arg, command.name()))
        return command.execute(args)

    def execute_method(self, method: Callable, msg: str):
        return method(msg)


class Session:

    def __init__(self, controller: ResponseController, sender: Callable = None):        
        self.__controllers = [ControllerExecutor(controller)]    
        self.__set_response_action(None)
        self.__sender = sender

    def __set_response_action(self, action: Callable):        
        self.__response_action = action

    def __get_response_action(self) -> Callable:        
        return self.__response_action

    def process(self, msg: str) -> Response:        
        response = None            

        response_action = self.__get_response_action()        
        if response_action is not None:
            response = self.__controllers[-1].execute_method(response_action, msg)
            self.__set_response_action(None)        

        if response is None:
            response = self.__controllers[-1].execute(msg)

        if msg in ["help", "/help"]:
            response = self.__help()            

        if response is None:
            log.error("Unknown message: '%s'" % msg)
            return ResponseMessage("Don't know what is '%s'" % msg)        

        return self.__process_response(response)

    def __process_response(self, response: Response):                
        if isinstance(response, str) or isinstance(response, ReplyMarkup):
            return ResponseMessage(response)
        elif response.response_action() is not None:            
            self.__set_response_action(response.response_action())
        if isinstance(response, ResponseAsync):
            bg_thread = Thread(target=self.__async_wrapper, args=[response])
            bg_thread.start()
            return response
        if isinstance(response, ResponseTerminateSession):
            self.__controllers.pop()
            return self.__hello()
        if isinstance(response, ResponseController):            
            self.__controllers.append(ControllerExecutor(response.controller()))            
            return self.__hello()
        
        return response
    
    def __hello(self):
        response = self.__controllers[-1].execute("hello")        
        if response is None:
            return "Greetings! You can customize this message in hello()"            
        else:
            return response

    def __async_wrapper(self, response):
        msg = self.__process_response(response.run_task())
        if msg is not None:
            self.__sender(msg)

    def __help(self) -> ResponseMessage:
        commands = self.__controllers[-1].commands()
        return ResponseMessage("\n".join(["%s - %s" % (command.name(), command.help())
                                          for command in commands if command.help() is not '']))
