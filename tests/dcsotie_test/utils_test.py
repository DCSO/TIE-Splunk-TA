# Copyright (c) 2020, DCSO GmbH

import os
import sys
import unittest

from dcsotie.utils import APIRelationshipLinks

TEST_LINK_HEADER = '''
<https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=60>; rel=previous, <https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=100>; rel=next, <https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=680>; rel=last, <https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=0>; rel=first
'''

TEST_LINK_HEADER_EXP = {
    'first': 'https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=0',
    'last': 'https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=680',
    'next': 'https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=100',
    'previous': 'https://tie.dcso.de/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=60'}


class TestAPIRelationshipLinks(unittest.TestCase):
    def test_relationships(self):
        links = APIRelationshipLinks(TEST_LINK_HEADER)
        self.assertEqual(len(TEST_LINK_HEADER_EXP), len(links.as_dict()))
        have_keys = sorted([k for k in links.as_dict()])
        exp_keys = sorted([k for k in TEST_LINK_HEADER_EXP])

        self.assertEqual(exp_keys, have_keys)
        for rel, link in links.as_dict().items():
            self.assertEqual(TEST_LINK_HEADER_EXP[rel], link)

    def test_relationships_are_optional(self):
        links = APIRelationshipLinks("<https://next>; rel=next, <https://previous>; rel=previous")
        self.assertIsNone(links.first)
        self.assertIsNone(links.last)
        self.assertIsNotNone(links.next)
        self.assertIsNotNone(links.previous)


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', "lib"))
    unittest.main()
