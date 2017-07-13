import abc
from stan import StanJoinedData, StanFlatData


class ParserError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Parser(abc.ABC):

    @abc.abstractmethod
    def parse(self, file_path: str):
        """ Parsing a file """

    @abc.abstractmethod
    def get_stat(self, data_format: str) -> StanJoinedData or StanFlatData:
        """ Returns stat data """
