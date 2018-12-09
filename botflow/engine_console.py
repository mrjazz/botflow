from botflow.engine_telegram import ResponseButtons
from botflow.session import Session, Response


class ConsoleEngine:

    def __init__(self, controller):
        self.__session = Session(controller, lambda msg: print(msg))

    def run(self):
        print("Welcome!")
        while True:
            request = input()
            self.process(request)

    def process(self, request):
        response = self.__session.process(request)
        if isinstance(response, ResponseButtons):
            for i in response.markup().inline_keyboard:
                print("[%s]" % i[0].text)
        if issubclass(response.__class__, Response):
            print(response.msg())
        else:
            print("Unknown request: {}".format(request))

