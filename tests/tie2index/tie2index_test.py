# Copyright (c) 2020, DCSO GmbH

import io
import json
import os
import sys
import unittest

try:
    import dcsotie
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', "lib"))

from dcsotiesplunk.config import default_configuration
from dcsotie.utils import Range
from dcsotiesplunk.filtering import filter_iocs

test_filter_data = {
    'iocs': [
        {'test_case': 1, 'data_type': "IPv4", 'min_severity': 1, 'max_severity': 3, 'min_confidence': 30,
         'max_confidence': 80},
        {'test_case': 2, 'data_type': "IPv4", 'min_severity': 0, 'max_severity': 0, 'min_confidence': 10,
         'max_confidence': 30},
        {'test_case': 3, 'data_type': "IPv4", 'min_severity': 0, 'max_severity': 0, 'min_confidence': 10,
         'max_confidence': 30},
        {'test_case': 4, 'data_type': "DomainName", 'min_severity': 2, 'max_severity': 5, 'min_confidence': 40,
         'max_confidence': 90},
        {'test_case': 5, 'data_type': "DomainName", 'min_severity': 0, 'max_severity': 0, 'min_confidence': 10,
         'max_confidence': 30},
        {'test_case': 5.1, 'data_type': "DomainName", 'min_severity': 0, 'max_severity': 0, 'min_confidence': 10,
         'max_confidence': 90},
        {'test_case': 6, 'data_type': "URLVerbatim", 'min_severity': 2, 'max_severity': 5, 'min_confidence': 40,
         'max_confidence': 90},
        {'test_case': 7, 'data_type': "URLVerbatim", 'min_severity': 0, 'max_severity': 0, 'min_confidence': 10,
         'max_confidence': 80},
        {'test_case': 8, 'data_type': "URLVerbatim", 'min_severity': 1, 'max_severity': 3, 'min_confidence': 10,
         'max_confidence': 80},
    ],
}


def filter_result_cases(fp: io.StringIO):
    lines = fp.getvalue().splitlines(keepends=False)
    return sorted([json.loads(l)['test_case'] for l in lines])


class TestTie2Index(unittest.TestCase):
    def test_filter_iocs(self):
        setup = default_configuration()

        fp = io.StringIO()
        filter_iocs(test_filter_data['iocs'], setup['filter'], fp)

        self.assertEqual([1, 4, 6, 8], filter_result_cases(fp))

    def test_filter_iocs_with_non_malicious_url_verbatim(self):
        setup = default_configuration()
        setup['filter']['url_severity'] = Range(0)

        fp = io.StringIO()
        filter_iocs(test_filter_data['iocs'], setup['filter'], fp)

        self.assertEqual([1, 4, 6, 7, 8], filter_result_cases(fp))

    def test_filter_iocs_with_non_malicious_domain_name(self):
        setup = default_configuration()
        setup['filter']['dom_severity'] = Range(0)

        fp = io.StringIO()
        filter_iocs(test_filter_data['iocs'], setup['filter'], fp)

        self.assertEqual([1, 4, 5.1, 6, 8], filter_result_cases(fp))


if __name__ == '__main__':
    unittest.main()
