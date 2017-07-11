from .parser import Parser, ParserError
import datetime
from xml.etree.ElementTree import iterparse
from tqdm import tqdm

# In various DTD version may be various CPU tag name
CPU_SECTION_NAMES = {'cpu-load-all', 'cpu-load'}


class SarXmlParser(Parser):
    """
    XML parser for stat files from sar util (sysstat package)
    Optimized for working with big files. Not so fast, but saving memory.

    Main public methods: parse() and get_stat()

    sar start example:
    sar -A 1 -o bin_file
    Extract data from binary to xml:
    sadf -x bin_file -- -A > output.xml

    Usage example:
    sar = SarXmlParser()  # Create instance
    sar.parse(xml_file_path)  # Parsing
    stat = sar.get_stat(data_format='joined')  # Return stats with needed format
    """

    def __init__(self):
        """
        Class constructor
        """
        self.file_path = None
        self.stat_length = None

        self.iterparse_context = None

        self.sysstat_data_version = None
        self.hostname = None
        self.sysname = None
        self.release = None
        self.machine = None
        self.cpu_count = None

        self.__current_timestamp = None

        # Main dict for saving extracted data
        self.data = dict()

    def parse(self, file_path: str, sections: set = {'cpu', 'mem', 'io', 'disk', 'fs'}):
        if self.file_path is not None:  # instance reset for repeated usage
            self.__init__()

        self.file_path = file_path

        if not sections.issubset({'cpu', 'mem', 'io', 'disk', 'fs'}):
            raise ParserError('Incorrect sections')

        for section in sections:
            self.data[section] = dict()

        # Calc stat length by "timestamp" tag. Needed for progress bar (tqdm).
        with open(self.file_path, 'r') as stat_file:
            print('Calculating sar stat length...')
            self.stat_length = sum(1 if line.strip() == '</timestamp>' else 0 for line in stat_file)
            print('Sar stat length: {}'.format(self.stat_length))

        # Create iterparse context and skip root. Tracks "start" and "end" events for partitions.
        self.iterparse_context = iter(iterparse(self.file_path, events=('start', 'end')))
        next(self.iterparse_context)  # Skip root

        # Read main header
        for event, element in self.iterparse_context:
            if event == 'start' and element.tag == 'sysdata-version':
                self.sysstat_data_version = element.text
            elif event == 'start' and element.tag == 'host':
                self.hostname = element.get('nodename')
            elif event == 'start' and element.tag == 'sysname':
                self.sysname = element.text
            elif event == 'start' and element.tag == 'release':
                self.release = element.text
            elif event == 'start' and element.tag == 'machine':
                self.machine = element.text
            elif event == 'start' and element.tag == 'number-of-cpus':
                self.cpu_count = int(element.text)
            elif event == 'start' and element.tag == 'statistics':
                break

        with tqdm(desc='Analyzing sar stat', total=self.stat_length) as pbar:
            for event, element in self.iterparse_context:
                if event == 'end' and element.tag == 'timestamp':
                    dt = element.get('date') + '_' + element.get('time').replace('-',':')
                    self.data.setdefault('timestamp', [])\
                        .append(int(datetime.datetime.strptime(dt, "%Y-%m-%d_%H:%M:%S").timestamp()))
                    self._parse_stat(list(element), sections)
                    element.clear()
                    pbar.update(1)
                elif event == 'end' and element.tag == 'statistics':
                    break

    def _parse_cpu(self, element_list):
        """
        Private method for parse CPU section

        :param element_list: section context
        """
        for element in element_list:
            attributes = element.attrib
            for attribute in attributes:
                if attribute != 'number':
                    self.data['cpu'].setdefault('_'.join(['cpu', attributes['number']]), dict()).setdefault(attribute, [])\
                        .append(float(attributes[attribute].replace(',', '.')))
            self.data['cpu'].setdefault('_'.join(['cpu', attributes['number']]), dict()).setdefault('util', [])\
                .append(100.0-float(attributes['idle'].replace(',', '.')))

    def _parse_mem(self, element_list):
        """
        Private method for parse memory section

        :param element_list: section context
        """
        for element in element_list:
            self.data['mem'].setdefault(element.tag.replace('-', '_'), []).append(float(element.text.replace(',', '.')))

    def _parse_io(self, element_list):
        """
        Private method for parse IO section

        :param element_list: section context
        """
        for element in element_list:
            if element.tag == 'tps':
                self.data['io'].setdefault('tps', []).append(float(element.text.replace(',', '.')))
            elif element.tag == 'io-reads':
                self.data['io'].setdefault('rtps', []).append(float(element.get('rtps').replace(',', '.')))
                self.data['io'].setdefault('bread', []).append(float(element.get('bread').replace(',', '.')))
            elif element.tag == 'io-writes':
                self.data['io'].setdefault('wtps', []).append(float(element.get('wtps').replace(',', '.')))
                self.data['io'].setdefault('bwrtn', []).append(float(element.get('bwrtn').replace(',', '.')))

    def _parse_disk(self, element_list):
        """
        Private method for parse disk section

        :param element_list: section context
        """
        for element in element_list:
            attributes = element.attrib
            for attribute in attributes:
                if attribute != 'dev':
                    self.data['disk'].setdefault(attributes['dev'], dict()).setdefault(attribute, [])\
                        .append(float(attributes[attribute].replace(',', '.')))

    def _parse_network(self, element_list):
        """
        Private method for parse network section

        :param element_list: section context
        """
        for element in element_list:
            pass

    def _parse_filesystems(self, element_list):
        """
        Private method for parse filesystems section

        :param element_list: section context
        """
        for element in element_list:
            attributes = element.attrib
            for attribute in attributes:
                if attribute != 'fsname':
                    self.data['fs'].setdefault(attributes['fsname'], dict()).setdefault(attribute, []) \
                        .append(float(attributes[attribute].replace(',', '.')))

    def _parse_stat(self, element_list, sections):
        """
        Private method for parse "timestamp" section

        There are sections with metrics inside this section.
        To analyze each, a separate private method is called.

        :param element_list: section context
        :param sections: set of sections that will be analyzed
        """
        # TODO: Implement parsing for other metrics
        for element in element_list:
            if element.tag in CPU_SECTION_NAMES and 'cpu' in sections:
                self._parse_cpu(list(element))
            elif element.tag == 'io' and 'io' in sections:
                self._parse_io(list(element))
            elif element.tag == 'memory' and 'mem' in sections:
                self._parse_mem(list(element))
            elif element.tag == 'disk' and 'io' in sections:
                self._parse_disk(list(element))
            elif element.tag == 'filesystems' and 'fs' in sections:
                self._parse_filesystems(list(element))

    def _extract_data(self, section_key, data_offset):
        """
        Extracts all metrics from specified section in self.data by offset

        :param section_key: section name
        :param data_offset: offset in metrics lists
        :return: dict of section with data from all metrics lists by offset
        """
        if section_key in {'cpu', 'disk', 'fs'}:
            return {section: {metric: self.data[section_key][section][metric][data_offset]
                              for metric in self.data[section_key][section]}
                    for section in self.data[section_key]}
        elif section_key in {'mem', 'io'}:
            return {metric: self.data[section_key][metric][data_offset] for metric in self.data[section_key]}
        else:
            raise ParserError('Unknown section: {}'.format(section_key))

    def get_stat(self, data_format='flat', time_zone_correction=0):
        """
        Return stat data with specified format. Available formats: 'flat', 'joined'

        'flat' format:
        dict(timestamp=list(),
             section_key_1=dict(),
             section_key_2=dict(),
             section_key_3=dict(),
             ...)
        Feature: Every metric in any section is a list(), as well as timestamps in the root of the dict.
                 All metrics have a positional relationship with timestamps.
        Advantage: Convenient for direct drawing of graphs.

        'joined' format:
        dict(timestamp_1=dict(section_key_1=dict(), section_key_2=dict()),
             timestamp_2=dict(section_key_1=dict(), section_key_2=dict()),
             timestamp_3=dict(section_key_1=dict(), section_key_2=dict()),
             ...)
        Feature: All metrics data are grouped by timestamp.
                 Each metric in the target section of the target timestamp is float.
        Advantage: Convenient for time correlation with other data

        :param data_format: return data format
        :param time_zone_correction: time zone correction by seconds
        :return: dict() of data with specified format
        """
        if data_format not in {'flat', 'joined'}:
            raise ParserError('Incorrect data format: {}'.format(data_format))

        if data_format == 'flat':
            # TODO: correction by time zone
            return self.data
        elif data_format == 'joined':
            return {ts + time_zone_correction: {section: self._extract_data(section, n)
                                                for section in self.data if section is not 'timestamp'}
                    for n, ts in enumerate(self.data['timestamp'])}
