from stan.parser import TlsmCsvParser
import os
import glob
from pprint import pprint

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILES = sorted(glob.glob(FILE_DIR + '/files/tlsm/*.csv'))

if __name__ == '__main__':
    print('\n******* Files for parse *******')
    pprint(TEST_FILES)

    parser = TlsmCsvParser()
    parser.parse(TEST_FILES)
    stat = parser.get_stat()

    print('\n******* Result *******')
    pprint(stat)
