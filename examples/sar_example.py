#!/usr/bin/env python3

from stan.parser import SarXmlParser
import os
import pprint

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = FILE_DIR + '/files/sar_DTDv2.19.xml'

if __name__ == '__main__':
    sar_parser = SarXmlParser()
    sar_parser.parse(TEST_XML)
    stat = sar_parser.get_stat(data_format='flat')
    print(sar_parser.hostname)
    pprint.pprint(stat)
