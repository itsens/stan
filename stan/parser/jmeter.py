from tqdm import tqdm
import datetime

from .parser import Parser, ParserError
from xml.etree.ElementTree import iterparse


class JmeterXmlParser(Parser):
    def __init__(self):
        self.file_path = None
        self.stat_length = None

        self.iterparse_context = None

        self.__current_timestamp = None

        self.data = dict()

        self.t = list()  # Load time: 115
        self.it = list()
        self.lt = list()  # Latency: 89
        self.ct = list()  # Connect Time: 51
        self.ts = list()
        self.ts = list()
        self.s = list()  # "true"
        self.lb = list()  # "HTTPR: login"
        self.rm = list()  # "OK"
        self.tn = list()  # "TG: get page 75 documents  1-1"
        self.dt = list()  # "text"
        self.de = list()  # "UTF-8"
        self.by = list()  # "21978"
        self.sby = list()  # "1479"
        self.sc = list()  # "1"
        self.ec = list()  # "0"
        self.ng = list()  # "1"
        self.na = list()  # "1"
        self.hn = list()  # "MSK-W0680" >

    def parse(self, file_path: str):
        if self.file_path is not None:
            self.__init__()

        self.file_path = file_path

        self.iterparse_context = iter(iterparse(self.file_path, events=('start', 'end')))
        next(self.iterparse_context)

        for event, element in self.iterparse_context:
            if event == 'end' and element.tag == 'httpSample':
                attributes = element.attrib
                for attribute in attributes:
                    if attribute == 't':
                        self.t.append(int(attributes[attribute]))
                    elif attribute == 'it':
                        self.it.append(int(attributes[attribute]))
                    elif attribute == 'lt':
                        self.ts.append(int(attributes[attribute]))
                    elif attribute == 'ts':
                        self.ts.append(int(attributes[attribute]))
                    elif attribute == 'ct':
                        self.ts.append(int(attributes[attribute]))

    def get_stat(self, data_format='flat', time_zone_correction=0):
        if data_format not in {'flat', 'joined'}:
            raise ParserError('Incorrect data format: {}'.format(data_format))

        if data_format == 'flat':
            # TODO: correction by time zone
            return dict(t=self.t,
                        it=self.it,
                        lt=self.lt,
                        ct=self.ct,
                        ts=self.ts)
        elif data_format == 'joined':
            return self.data
