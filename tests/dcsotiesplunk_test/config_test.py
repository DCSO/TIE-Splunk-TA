# Copyright (c) 2020, DCSO GmbH

import os
import sys
import unittest

from dcsotiesplunk.config import normalize_configuration, CONFIG_SCHEMA, default_configuration

TEST_LINK_HEADER = '''
<https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=60>; rel=previous, <https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=100>; rel=next, <https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=680>; rel=last, <https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=0>; rel=first
'''

TEST_LINK_HEADER_EXP = {
    'first': 'https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=0',
    'last': 'https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=680',
    'next': 'https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=100',
    'previous': 'https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=60'}


class TestNormalizeConfig(unittest.TestCase):
    def test_normalize(self):
        have = {
            'filter': {
                'url_severity': "3",
            }
        }

        res = normalize_configuration(have)
        self.assertIsInstance(res['filter']['url_severity'], int)
        self.assertEqual(3, res['filter']['url_severity'])
        self.assertEqual(CONFIG_SCHEMA['filter']['dom_confidence'][1], res['filter']['dom_confidence'])
        self.assertEqual(CONFIG_SCHEMA['tie']['feed_api'][1],
                         res['tie']['feed_api'])


class TestDefaultConf(unittest.TestCase):
    def test_default(self):
        res = default_configuration()
        self.assertEqual(CONFIG_SCHEMA['filter']['dom_confidence'][1], res['filter']['dom_confidence'])
        self.assertEqual(CONFIG_SCHEMA['tie']['feed_api'][1],
                         res['tie']['feed_api'])


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', "lib"))
    unittest.main()
