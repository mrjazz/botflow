# botflow

BotFlow is simple framework for building conversational interfaces.

For now supported only Telegram and Console as conversational gateways.

## An example of Bot code

```python
class MathController:

    def __init__(self):
        self.__result = 0
    
    def hello(self):
        return "Hi!"
    
    def delay(self):
        return ResponseAsync("Started...", lambda: time.sleep(3), done_action=lambda: "Done!")
    
    def validate(self, msg: str):
        if not msg.isdigit():
            return None
        if msg == self.__result:
            response = "correct"
        else:
            response = "incorrect"
        return ResponseAsync(response, lambda: time.sleep(1), done_action=self.quiz)
    
    def quiz(self):
        """
        @help this is quiz help
        """
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        self.__result = str(a + b)
        return ResponseMessage("%d+%d=?" % (a, b), response_action=self.validate)

    def do_repeat(self, params: str):
        if ResponseKeyboard.is_positive(params.lower()):
            return 'We are do it again!'
        else:
            return 'Sorry..'

    def do_exit(self):
        """
        @match exit
        @help terminate bot
        """
        logging.info("Terminating bot...")
        exit()
``` 