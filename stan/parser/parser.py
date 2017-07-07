import abc


class Parser(abc.ABC):

    @abc.abstractmethod
    def __init__(self, file_path: str):
        """ Constructor """

    @abc.abstractmethod
    def run(self):
        """ Starts parsing """

    @abc.abstractmethod
    def get(self, data_format: str) -> dict:
        """ Returns stat data or other information from header """
