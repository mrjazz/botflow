class Context:

    def __init__(self):
        self.__params = {}

    def set(self, key, value):
        self.__params.setdefault(key, value)

    def get(self, key):
        return self.__params.get(key)
