from .parser import Parser, ParserError
from stan import StanDict, StanJoinedData, StanFlatData
from collections import Iterable
from tqdm import tqdm
from os import path

# Common operations offsets
TIMESTAMP = 0
START_TIME_AND_PROCESS_ID = 1
THREAD_ID = 2
CONNECTION_ID = 3
OPERATION_CODE = 4

# Specific operations offsets
REQUEST_ID = 5
REQUEST_FILE_NAME = 6
SEND_DATA_ID = 6
SEND_DATA_SIZE = 7
REQUEST_SEND_DATA_SIZE = 6

RECV_DATA_ID = 6
RECV_DATA_SIZE = 7
RESPONSE_RECV_DATA_SIZE = 6

SSL_SEND_DATA_SIZE = 5
SSL_RECV_DATA_SIZE = 6

# Operations codes
START_ASYNC = '0'
SUCCESS_ASYNC = '1'
FAILED_ASYNC = '2'

START_SSL_HANDSHAKE = '3'
SUCCESS_SSL_HANDSHAKE = '4'
FAILED_SSL_HANDSHAKE = '5'

START_SEND_REQ = '6'
START_SEND_DATA = '7'
SUCCESS_SEND_DATA = '8'
FAILED_SEND_DATA = '9'
FINISH_SEND_REQ = '10'
FAILED_SEND_REQ = '11'

START_RECV_RSP = '12'
START_RECV_DATA = '13'
SUCCESS_RECV_DATA = '14'
FAILED_RECV_DATA = '15'
SUCCESS_RECV_RSP = '16'
FAILED_RECV_RSP = '17'

CLOSE_SSL_CONNECTION = '18'


class TlsmCsvParser(Parser):

    def __init__(self):
        self.sampling_interval = 's'

        self.tlsm_log_files = None
        self.tlsm_log_file = None

        self.data = StanJoinedData()
        self.file_data = StanJoinedData()

        self._connections_start_times = dict()
        self._success_tcp_connections = set()
        self._success_ssl_connections = set()
        self._failed_req_rsp_connections = set()

    def get_stat(self, data_format: str='flat') -> StanJoinedData or StanFlatData:

        pass

    def parse(self, file_paths: Iterable):
        for file in file_paths:
            if not path.isfile(file):
                raise ParserError('File does not exists: {}'.format(file))
            self.tlsm_log_file = file
            self._parse_file()

    def _parse_file(self):
        with open(self.tlsm_log_file, 'r') as stat_file:

            file_size = sum(1 for l in open(self.tlsm_log_file))
            desc = '{}'.format(path.basename(self.tlsm_log_file))

            for line in tqdm(stat_file, total=file_size, desc=desc):
                if line[0].isdigit():
                    operation = line.strip().split(';')
                    self._process_operation(operation)

    def _process_operation(self, operation: list):
        # Уникальный ID соединения в контексте всех процессов и потоков tls_meter
        connection_id = '_'.join([operation[THREAD_ID], operation[CONNECTION_ID]])

        operation_timestamp = int(operation[TIMESTAMP])
        operation_time_interval = self._get_time_interval(operation_timestamp)

        # Если первый или новый интервал, то добавляем новые записи в статистику
        if len(self.stat['timestamp']) == 0 or operation_time_interval > self.stat['timestamp'][-1]:
            self.stat['timestamp'].append(operation_time_interval)
            self.stat['tcp_connections_per_second'].append(0)
            self.stat['ssl_connections_per_second'].append(0)
            self.stat['throughput_upload'].append(0)
            self.stat['throughput_download'].append(0)
            self.stat['req_per_second'].append(0)
            self.stat['rsp_per_second'].append(0)
            self.stat['active_tcp_connections_count'].append(self.stat['active_tcp_connections_count'][-1]
                                                             if len(self.stat['active_tcp_connections_count']) != 0
                                                             else 0)
            self.stat['active_ssl_connections_count'].append(self.stat['active_ssl_connections_count'][-1]
                                                             if len(self.stat['active_ssl_connections_count']) != 0
                                                             else 0)

            self.stat['tcp_times'].append([])
            self.stat['ssl_handshake_times'].append([])
            self.stat['ttfb_times'].append([])
            self.stat['connection_times'].append([])

            self.stat['failed_tcp_per_second'].append(0)
            self.stat['failed_ssl_per_second'].append(0)
            self.stat['failed_req_per_second'].append(0)
            self.stat['failed_rsp_per_second'].append(0)
            self.stat['failed_total_per_second'].append(0)

        if operation[OPERATION_CODE] == START_ASYNC:
            self._connections_start_times[connection_id] = operation_timestamp
        elif operation[OPERATION_CODE] == SUCCESS_ASYNC:
            self.stat['tcp_connections_per_second'][-1] += 1
            self.stat['active_tcp_connections_count'][-1] += 1
            self._success_tcp_connections.add(connection_id)
            self.stat['tcp_times'][-1].append(operation_timestamp - self._connections_start_times[connection_id])
        elif operation[OPERATION_CODE] == FAILED_ASYNC:
            self.stat['failed_tcp_per_second'][-1] += 1
            self.stat['failed_total_per_second'][-1] += 1
        elif operation[OPERATION_CODE] == START_SSL_HANDSHAKE:
            pass
        elif operation[OPERATION_CODE] == SUCCESS_SSL_HANDSHAKE:
            self.stat['ssl_connections_per_second'][-1] += 1
            self.stat['active_ssl_connections_count'][-1] += 1
            self._success_ssl_connections.add(connection_id)
            self.stat['ssl_handshake_times'][-1].append(operation_timestamp - self._connections_start_times[connection_id])
        elif operation[OPERATION_CODE] == FAILED_SSL_HANDSHAKE:
            self.stat['failed_ssl_per_second'][-1] += 1
            self.stat['failed_total_per_second'][-1] += 1
        elif operation[OPERATION_CODE] == START_SEND_REQ:
            pass
        elif operation[OPERATION_CODE] == START_SEND_DATA:
            pass
        elif operation[OPERATION_CODE] == SUCCESS_SEND_DATA:
            self.stat['throughput_upload'][-1] += int(operation[SEND_DATA_SIZE])
        elif operation[OPERATION_CODE] == FAILED_SEND_DATA:
            pass
        elif operation[OPERATION_CODE] == FINISH_SEND_REQ:
            self.stat['req_per_second'][-1] += 1
        elif operation[OPERATION_CODE] == FAILED_SEND_REQ:
            self.stat['failed_req_per_second'][-1] += 1
            self.stat['failed_total_per_second'][-1] += 1
            self._failed_req_rsp_connections.add(connection_id)
        elif operation[OPERATION_CODE] == START_RECV_RSP:
            if operation[REQUEST_ID] == '1':
                self.stat['ttfb_times'][-1].append(operation_timestamp - self._connections_start_times[connection_id])
        elif operation[OPERATION_CODE] == START_RECV_DATA:
            pass
        elif operation[OPERATION_CODE] == SUCCESS_RECV_DATA:
            self.stat['throughput_download'][-1] += int(operation[RECV_DATA_SIZE])
        elif operation[OPERATION_CODE] == FAILED_RECV_DATA:
            pass
        elif operation[OPERATION_CODE] == SUCCESS_RECV_RSP:
            self.stat['rsp_per_second'][-1] += 1
        elif operation[OPERATION_CODE] == FAILED_RECV_RSP:
            self.stat['failed_rsp_per_second'][-1] += 1
            self.stat['failed_total_per_second'][-1] += 1
            self._failed_req_rsp_connections.add(connection_id)
        elif operation[OPERATION_CODE] == CLOSE_SSL_CONNECTION:
            if connection_id in self._success_tcp_connections:
                self.stat['active_tcp_connections_count'][-1] -= 1
            if connection_id in self._success_ssl_connections:
                self.stat['active_ssl_connections_count'][-1] -= 1
            if connection_id not in self._failed_req_rsp_connections:
                self.stat['connection_times'][-1].append(operation_timestamp - self._connections_start_times[connection_id])

    def _get_time_interval(self, timestamp: int) -> int:
        """
        "Округляет" временную метку до указанного интервала

        :param timestamp: временная метка (Unix timestamp), нс
        :return: метка временного интервала
        """
        # TODO: расширить поддерживаемые интервалы усреднения
        if self.sampling_interval == 's':
            return timestamp//10**9
