from pprint import pprint

__author__ = 'borodenkov.e.a@gmail.com'

from .parser import Parser, ParserError
from xml.etree.ElementTree import iterparse
from tqdm import tqdm
from stan import StanData, StanDict
import datetime
import os
import sys
import stat
import genericpath
from genericpath import *
from stan import StanDict, StanData
from .parser import Parser, ParserError
from tqdm import tqdm
from os import path
from collections import Iterable

TIMESTAMP = 0  # сюда ложим первую временную метку


class JMeterStatFile:
    def __init__(self, file_path):

        self.file_path = None
        self.stat_length = None
        self.log_file = file_path
        self.sampling_interval = 's'

        self.iterparse_context = None

        self.__current_timestamp = None

        self.data = dict()


        # словарь для удобства парсинга исходного файла
        self.metrics = {'load_time': 't',
                        'latency': 'lt',
                        'connect_time': 'ct',
                        'timestamp': 'ts',
                        'label': 'lb',
                        'tread_group': 'tg',
                        'size_in_bytes': 'by',
                        'sent_bytes': 'sby',
                        'error_count': 'ec'
                        }

        # словарь для
        self.stat = dict(t=[],
                         lt=[],
                         ct=[],
                         ts=[],
                         tg=[],
                         lb=[],
                         by=[],
                         sby=[],
                         ec=[])

        self.load_time = list()  # Load time: 115
        self.it = list()
        self.latency = list()  # Latency: 89
        self.connect_time = list()  # Connect Time: 51
        self.timestamp = list()
        self.timestamp2 = list()
        self.s = list()  # "true"
        self.label = list()  # "HTTPR: login"
        self.rm = list()  # "OK"
        self.tread_group = list()  # "TG: get page 75 documents  1-1"
        self.dt = list()  # "text"
        self.de = list()  # "UTF-8"
        self.size_in_byte = list()  # "21978" Size in bytes: 21978
        self.sent_bytes = list()  # "1479" Sent bytes:1479
        self.sc = list()  # "1"
        self.error_count = list()  # Error Count: 0
        self.ng = list()  # "1"
        self.na = list()  # "1"
        self.hn = list()  # "MSK-W0680" >

        self.rps = list()  # для хранения запросов в секунду

    # def _get_time_interval(self, timestamp: int) -> int:
    #     if self.sampling_interval == 's':
    #         return timestamp # // 10 ** 9
    #
    # def _process_operation(self, operation: dict):
    #     print(int(operation[TIMESTAMP]) )
    #     operation_timestamp = int(operation[TIMESTAMP])  # переменная для хранения первой временной метки
    #     operation_time_interval = self._get_time_interval(
    #         operation_timestamp)  # временной интервал для агригации данных (1с)
    #
    #     if len(self.stat['ts']) == 0 or operation_time_interval > self.stat['ts'][-1]:
    #         self.stat['ts'].append(operation_time_interval)
    #         self.stat['lt'].append(0)
    #         print(self.stat)


    def parse(self):
        with open(self.log_file, 'r') as stat_file:

            self.file_path = self.log_file

            self.iterparse_context = iter(iterparse(self.file_path, events=('start', 'end')))
            next(self.iterparse_context)

            for event, element in self.iterparse_context:
                if event == 'end' and element.tag == 'httpSample':
                    attributes = element.attrib
                    for attribute in attributes:
                        if attribute == self.metrics['load_time']:
                            self.load_time.append(int(attributes[attribute]))
                        elif attribute == 'it':
                            self.it.append(int(attributes[attribute]))
                        elif attribute == self.metrics['latency']:
                            self.latency.append(int(attributes[attribute]))
                        elif attribute == self.metrics['timestamp']:
                            self.timestamp.append(int(attributes[attribute]))
                        elif attribute == self.metrics['connect_time']:
                            self.connect_time.append(int(attributes[attribute]))
                        elif attribute == self.metrics['label']:
                            self.label.append(attributes[attribute])
                        elif attribute == self.metrics['size_in_bytes']:
                            self.size_in_byte.append(int(attributes[attribute]))
                        elif attribute == self.metrics['sent_bytes']:
                            self.sent_bytes.append(int(attributes[attribute]))
                        elif attribute == self.metrics['error_count']:
                            self.error_count.append(int(attributes[attribute]))

        # self.timestamp2 = [int(number/1000) for number in self.timestamp]
        # print(self.timestamp2)
        # print(self.timestamp)
        self.stat = dict(load_time=self.load_time,
                         it=self.it,
                         latency=self.latency,
                         connect_time=self.connect_time,
                         label=self.label,
                         size_in_bytes=self.size_in_byte,
                         sent_bytes=self.sent_bytes,
                         error_count=self.error_count,
                         timestamp=self.timestamp)

        return {ts: {metric: self.stat[metric][n]
                     for metric in self.stat if metric is not 'timestamp'}
                for n, ts in enumerate(self.stat['timestamp'])}


class JMeterXmlParser2(Parser):
    def __init__(self):
        self.stat_files = None
        self.stat = dict()

    def parse(self, file_paths: Iterable):
        if self.stat_files is not None:
            self.__init__()

        self.stat_files = file_paths  # указываем директорию откуда парсить

        for file in tqdm(self.stat_files, desc='Total'):

            stat = JMeterStatFile(file)  # инициализируем класс парсинга
            _stat = stat.parse()

            # print('входящий словарь:    ', _stat)
            # print('начинаем разворачивать:  ')

            for time in _stat:
                # print(self.stat)
                if time in self.stat:
                    for metric in _stat[time]:
                        self.stat[time][metric] += _stat[time][metric]
                else:
                    pass
                    self.stat[time] = _stat[time]

    def get_stat(self) -> StanData:
        result = StanData()
        for ts in self.stat:
            metrics = StanDict()
            for metric in self.stat[ts]:
                metrics[metric] = self.stat[ts][metric]
            result.append(ts, metrics)

        return result
