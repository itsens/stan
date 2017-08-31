from .parser import Parser, ParserError
from stan import StanData, StanDict
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
    stat = sar.get_stat(data_format='joined')  # Return stats with specified format
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

        # Main structure for saving extracted data
        self.data = StanData()
        self.__metrics = None

    def parse(self, file_path: str, sections: set = {'cpu', 'mem', 'io', 'disk', 'net', 'fs', 'queue'}):
        if self.file_path is not None:  # instance reset for repeated usage
            self.__init__()

        self.file_path = file_path

        if not sections.issubset({'cpu', 'mem', 'io', 'disk', 'net', 'fs', 'queue'}):
            raise ParserError('Incorrect sections')

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
                    dt = element.get('date') + '_' + element.get('time').replace('-', ':')
                    ts = int(datetime.datetime.strptime(dt, "%Y-%m-%d_%H:%M:%S").timestamp())
                    self.__metrics = StanDict()
                    self._parse_stat(list(element), sections)
                    self.data.append(ts, self.__metrics)
                    element.clear()
                    pbar.update(1)
                elif event == 'end' and element.tag == 'statistics':
                    break

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
            elif element.tag == 'network' and 'net' in sections:
                self._parse_network(list(element))
            elif element.tag == 'filesystems' and 'fs' in sections:
                self._parse_filesystems(list(element))
            elif element.tag == 'queue' and 'queue' in sections:
                self._parse_queue(element)

    def _parse_cpu(self, element_list):
        """
        Private method for parse CPU section
        :param element_list: section context
        """
        for element in element_list:
            attributes = element.attrib
            for attribute in attributes:
                if attribute != 'number':
                    metric_key = 'cpu_' + attributes['number'] + '_' + attribute
                    self.__metrics[metric_key] = float(attributes[attribute].replace(',', '.'))
            metric_key = 'cpu_' + attributes['number'] + '_util'
            self.__metrics[metric_key] = 100.0 - float(attributes['idle'].replace(',', '.'))

    def _parse_mem(self, element_list):
        """
        Private method for parse memory section
        :param element_list: section context
        """
        for element in element_list:
            metric_key = 'mem_' + element.tag
            self.__metrics[metric_key] = float(element.text.replace(',', '.'))

    def _parse_io(self, element_list):
        """
        Private method for parse IO section
        :param element_list: section context
        """
        for element in element_list:
            if element.tag == 'tps':
                self.__metrics['io_tps'] = float(element.text.replace(',', '.'))
            elif element.tag == 'io-reads':
                self.__metrics['io_rtps'] = float(element.get('rtps').replace(',', '.'))
                self.__metrics['io_bread'] = float(element.get('bread').replace(',', '.'))
            elif element.tag == 'io-writes':
                self.__metrics['io_wtps'] = float(element.get('wtps').replace(',', '.'))
                self.__metrics['io_bwrtn'] = float(element.get('bwrtn').replace(',', '.'))

    def _parse_disk(self, element_list):
        """
        Private method for parse disk section
        :param element_list: section context
        """
        for element in element_list:
            attributes = element.attrib
            for attribute in attributes:
                if attribute != 'dev':
                    metric_key = 'disk_' + attributes['dev'] + '_' + attribute
                    self.__metrics[metric_key] = float(attributes[attribute].replace(',', '.'))

    def _parse_network(self, element_list):
        """
        Private method for parse network section
        :param element_list: section context
        """
        for element in element_list:
            attributes = element.attrib
            if element.tag in {'net-dev', 'net-edev'}:
                for attribute in attributes:
                    if attribute != 'iface':
                        metric_key = element.tag.replace('-', '_') + '_' + attributes['iface'] + '_' + attribute
                        self.__metrics[metric_key] = float(attributes[attribute].replace(',', '.'))
            else:
                for attribute in attributes:
                    metric_key = element.tag.replace('-', '_') + '_' + attribute
                    self.__metrics[metric_key] = float(attributes[attribute].replace(',', '.'))

    def _parse_filesystems(self, element_list):
        """
        Private method for parse filesystems section
        :param element_list: section context
        """
        for element in element_list:
            attributes = element.attrib
            for attribute in attributes:
                if attribute != 'fsname':
                    metric_key = 'fs_' + attributes['fsname'].split('/')[-1] + '_' + attribute
                    self.__metrics[metric_key] = float(attributes[attribute].replace(',', '.'))

    def _parse_queue(self, elements):
        '''
        Private method for parse filesystems section

        <queue runq-sz="0" plist-sz="452" ldavg-1="0,06" ldavg-5="0,14" ldavg-15="0,17" blocked="0"/>
        :param elements: section context
        '''
        attributes = elements.attrib
        for attribute in attributes:
            metric_key = 'queue_' + attribute
            self.__metrics[metric_key] = float(attributes[attribute].replace(',', '.'))

    def get_stat(self):
        """
        Return stat data in StanData structure

        :return: StanData
        """
        return self.data
