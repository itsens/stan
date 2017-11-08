__autor__ = 'borodenkov.e.a@gmail.com'

from .parser import Parser, ParserError
from xml.etree.ElementTree import iterparse


class JmeterXmlParser(Parser):
    """
    XML parser for stat files from jmeter util.

    example string:
    <httpSample t="3802" it="0" lt="3794" ct="4" ts="1499763762509"
                s="true" lb="HTTPR: documents" rm="OK" tn="TG: get page 75 documents  1-1"
                dt="text" de="" by="238961" sby="547" sc="1" ec="0" ng="1" na="1" hn="MSK-W0680">
    </httpSample>

    """
    def __init__(self):
        self.file_path = None
        self.stat_length = None

        self.iterparse_context = None

        self.__current_timestamp = None

        self.data = dict()

        self.metrics = {'load_time': 't',
                        'latency': 'lt',
                        'connect_time': 'ct',
                        'timestamp': 'ts',
                        'label': 'lb',
                        'tread_group': 'tn',
                        'size_in_bytes': 'by',
                        'sent_bytes': 'sby',
                        'error_count': 'ec'
                        }
        self.load_time = list()  # Load time: 115
        self.it = list()
        self.latency = list()  # Latency: 89
        self.connect_time = list()  # Connect Time: 51
        self.timestamp = list()
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

    def get_stat(self, data_format='flat', time_zone_correction=0):
        """
        return stat data with specified format.

        'flat' format:
        dict{timestamp=dict(),
            section_key_1=dict(),
            section_key_2=dict()
            ...}
        :param data_format: return data format
        :param time_zone_correction:
        :return: list() of data with specified format
        """
        if data_format not in {'flat', 'joined'}:
            raise ParserError('Incorrect data format: {}'.format(data_format))

        if data_format == 'flat':
            return dict(t=self.load_time,
                        it=self.it,
                        lt=self.latency,
                        ct=self.connect_time,
                        lb=self.label,
                        by=self.size_in_byte,
                        sby=self.sent_bytes,
                        ec=self.error_count,
                        ts=self.timestamp)
        elif data_format == 'joined':
            # TODO: реализовать
            return self.data

class JmeterCsvParser(Parser):
    def __init__(self, DIR_PATH, member=''):
        file = gzip.GzipFile(DIR_PATH, 'rb')
        if file.myfileobj.read(2) == '\037\213':
            file.myfileobj.seek(0)
            buffer = ""
            while 1:
                data = file.read()
                if data == "":
                    break
                buffer += data
            object = cPickle.loads(buffer)

            self.__dict__ = object.__dict__
        else:
            self.df = self.jmeter2pandas(DIR_PATH, member)
        file.close()

    def save(self, filepath="", bin=1):
        """Saves a compressed object to disk
        """
        if exists(filepath):
            print("Error: File " + filepath + "already exists")
        else:
            file = gzip.GzipFile(filepath, 'wb')
            file.write(cPickle.dumps(self, bin))
            file.close()

    def jmeter2pandas(self, DIR_PATH, member=''):

        read_csv_param = dict(index_col=['timeStamp'],
                              low_memory=False,
                              na_values=[' ', '', 'null'],
                              converters={'timeStamp': lambda a: float(a) / 1000}) # ,tp

        if member and zipfile.is_zipfile(DIR_PATH):
            zipy = zipfile.ZipFile(DIR_PATH)
            f = zipy.open(member, 'r')
            dfs = pd.read_csv(f, **read_csv_param)
            f.close()
            return dfs

        if isdir(DIR_PATH):
            files = filter(lambda a: '.csv' in a, listdir(DIR_PATH))

            dfs = pd.read_csv(DIR_PATH + files[0], **read_csv_param)
            for csvfile in files[1:]:
                dfs = dfs.append(
                    pd.read_csv(DIR_PATH + csvfile, **read_csv_param))
        else:
            dfs = pd.read_csv(DIR_PATH, **read_csv_param)

        return dfs

    def tmstmp_round(self, t):
        u""" Добавить столбец округлений timeStamp_round с агрегацией t сек"""
        self.df['timeStamp_round'] = [round(a / t) * t for a in self.df.index]
        self.agg = t

    def __getitem__(self, g):
        hjk = self.df[self.df.label == g]
        return hjk['elapsed'].groupby(hjk.index.map(lambda a: round(a / 1) * 1)).mean()