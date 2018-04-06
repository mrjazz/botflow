from abc import ABC, abstractmethod
from typing import Callable, Dict
from botflow.response import Response


class Command(ABC):

    @abstractmethod
    def execute(self, msg: str) -> Response:
        return None


