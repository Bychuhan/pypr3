from abc import ABC, abstractmethod
from typing import IO


from pydantic import BaseModel


class InfoParser(ABC):
    @staticmethod
    @abstractmethod
    def load(fp: IO[str]) -> BaseModel:
        pass

    @staticmethod
    @abstractmethod
    def loads(data: str) -> BaseModel:
        pass
