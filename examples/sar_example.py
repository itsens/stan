#!/usr/bin/env python3

from stan.parser import SarXmlParser
import os
from pprint import pprint

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = 'sar_g2g.xml'

if __name__ == '__main__':
    sar_parser = SarXmlParser()
    sar_parser.parse(TEST_XML)
    stat = sar_parser.get_stat()
    print(sar_parser.hostname)
