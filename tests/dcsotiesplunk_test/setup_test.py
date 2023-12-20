# Copyright (c) 2020, 2023, DCSO GmbH

import sys
import os
import unittest

try:
    import dcsotie
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from dcsotie.errors import TIEConfigError
from dcsotiesplunk.config import normalize_splunk_setup_args


class TestNormalizeSetup(unittest.TestCase):
    def test_client_id(self):
        with self.assertRaises(TIEConfigError) as ctx:
            normalize_splunk_setup_args(
                {"client_id": [""]}, labels={"client_id": "API client_id"}
            )

        self.assertIn("API client_id is required", str(ctx.exception))

        try:
            normalize_splunk_setup_args(
                {"client_id": ["somevalueforclient_id"]},
                labels={"client_id": "API client_id"},
            )
        except TIEConfigError as exc:
            self.fail("exception raised; except none (was {})".format(exc))

    def test_client_secret(self):
        with self.assertRaises(TIEConfigError) as ctx:
            normalize_splunk_setup_args(
                {"client_secret": [""]}, labels={"client_secret": "API client_secret"}
            )

        self.assertIn("API client_secret is required", str(ctx.exception))

        try:
            normalize_splunk_setup_args(
                {"client_secret": ["somevalueforclient_secret"]},
                labels={"client_id": "API client_secret"},
            )
        except TIEConfigError as exc:
            self.fail("exception raised; except none (was {})".format(exc))

    def test_updated_at_since(self):
        key = "updated_at_since"
        cases = [
            {"have": ["2006-01-02"], "exp": ["2006-01-02"]},
            {"have": ["2023-11-30T23:43:42Z"], "exp": ["2023-11-30T23:43:42Z"]},
        ]

        for i, case in enumerate(cases):
            data = {key: case["have"]}
            try:
                normalize_splunk_setup_args(data)
            except TIEConfigError as exc:
                self.fail("expected no exception for case #{}; got {}".format(i, exc))
            else:
                self.assertEqual(case["exp"], data[key])

        bad_cases = ["asdfasdf"]

        for i, case in enumerate(bad_cases):
            with self.assertRaises(
                TIEConfigError, msg="not raised for case #{}".format(i)
            ) as ctx:
                normalize_splunk_setup_args({key: case})

            self.assertIn(key, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
