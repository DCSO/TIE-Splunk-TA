# Copyright (c) 2020, DCSO GmbH

import sys
import os
import unittest

try:
    import dcsotie
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', "lib"))

from dcsotie.errors import TIEConfigError
from dcsotie.utils import Range, ConfidenceRange, SeverityRange
from dcsotiesplunk.config import normalize_splunk_setup_args


class TestNormalizeSetup(unittest.TestCase):
    def test_correct_severity_range(self):
        # configuration ending with `_severity` has Range values
        data = {
            'int_severity': 1,
            'str_severity': '6',
            'str_lower_severity': '1-',
            'str_upper_severity': '-4',
            'str_upper_lower_severity': '2-5',
        }

        exp_data = {
            'int_severity': SeverityRange(1),
            'str_severity': SeverityRange('6'),
            'str_lower_severity': SeverityRange('1-'),
            'str_upper_severity': SeverityRange('-4'),
            'str_upper_lower_severity': SeverityRange('2-5'),
        }

        normalize_splunk_setup_args(data)

        for k, v in data.items():
            self.assertIsInstance(v, SeverityRange, msg="{} not Range".format(k))
            self.assertEqual(exp_data[k], v)

    def test_incorrect_severity_range(self):
        data = [
            {'bad_severity': -2},  # negative integer
            {'bad_severity': '-bad'},
            {'bad_severity': 'bad-'},
            {'bad_severity': 'bad-bad'},
            {'bad_severity': '5-2'},
        ]

        for i, d in enumerate(data):
            with self.assertRaises(TIEConfigError, msg="not raised for case #{}".format(i)) as ctx:
                normalize_splunk_setup_args(d)

            self.assertIn('bad_severity', str(ctx.exception))

    def test_required_token(self):
        with self.assertRaises(TIEConfigError) as ctx:
            normalize_splunk_setup_args({'token': ''}, labels={'token': 'API Token'})

        self.assertIn("API Token is required", str(ctx.exception))

        try:
            normalize_splunk_setup_args({'token': 'somevaluefortoken'}, labels={'token': 'API Token'})
        except TIEConfigError as exc:
            self.fail("exception raised; except none (was {})".format(exc))

    def test_correct_confidence(self):
        # configuration ending with `_confidence` must be Range
        data = {
            'int_confidence': 30,
            'str_confidence': '60',
            'str_lower_confidence': '10-',
            'str_upper_confidence': '-40',
            'str_upper_lower_confidence': '20-80',
        }

        exp_data = {
            'int_confidence': ConfidenceRange(30),
            'str_confidence': ConfidenceRange('60'),
            'str_lower_confidence': ConfidenceRange('10-'),
            'str_upper_confidence': ConfidenceRange('-40'),
            'str_upper_lower_confidence': ConfidenceRange('20-80'),
        }

        normalize_splunk_setup_args(data)

        for k, v in data.items():
            self.assertIsInstance(v, ConfidenceRange, msg="{} not Range".format(k))
            self.assertEqual(exp_data[k], v, msg="Range {} != Range {}".format(v, exp_data[k]))

    def test_incorrect_confidence(self):
        data = [
            {'bad_confidence': -2},
            {'bad_confidence': 'bad'},
            {'bad_confidence': '10000'},
            {'bad_confidence': '-101'},
        ]

        for i, d in enumerate(data):
            with self.assertRaises(TIEConfigError, msg="not raised for case #{}".format(i)) as ctx:
                normalize_splunk_setup_args(d)

            self.assertIn('bad_confidence', str(ctx.exception))

    def test_start_ioc_seq(self):
        key = 'start_ioc_seq'
        cases = [
            {'have': 0, 'exp': 0},
            {'have': 12345, 'exp': 12345},
            {'have': '99999', 'exp': 99999},
        ]

        for i, case in enumerate(cases):
            data = {key: case['have']}
            try:
                normalize_splunk_setup_args(data)
            except TIEConfigError as exc:
                self.fail("expected no exception for case #{}; got {}".format(i, exc))
            else:
                self.assertEqual(case['exp'], data[key])

        bad_cases = ['asdfasdf', -1234, '-12345']

        for i, case in enumerate(bad_cases):
            with self.assertRaises(TIEConfigError, msg="not raised for case #{}".format(i)) as ctx:
                normalize_splunk_setup_args({key: case})

            self.assertIn(key, str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
