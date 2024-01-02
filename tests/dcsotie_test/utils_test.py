# Copyright (c) 2020, 2023, DCSO GmbH

import os
import sys
import unittest

try:
    import dcsotie
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from dcsotie.utils import APIRelationshipLinks, Range

TEST_LINK_HEADER = """
<https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=60>; rel=previous, <https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=100>; rel=next, <https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=680>; rel=last, <https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=0>; rel=first
"""

TEST_LINK_HEADER_EXP = {
    "first": "https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=0",
    "last": "https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=680",
    "next": "https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=100",
    "previous": "https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=60",
}


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
        links = APIRelationshipLinks(
            "<https://next>; rel=next, <https://previous>; rel=previous"
        )
        self.assertIsNone(links.first)
        self.assertIsNone(links.last)
        self.assertIsNotNone(links.next)
        self.assertIsNotNone(links.previous)


class TestRange(unittest.TestCase):
    def test_int(self):
        r = Range(3)
        self.assertEqual(3, r.lower)
        self.assertIsNone(r.upper)

        with self.assertRaises(ValueError):
            Range(-2)

    def test_tuple(self):
        r = Range((2, 5))
        self.assertEqual(2, r.lower)
        self.assertEqual(5, r.upper)
        self.assertTrue(r.in_range(3))

        with self.assertRaises(ValueError):
            Range((5, 2))

    def test_str_lower_upper(self):
        r = Range("2-5")
        self.assertEqual(2, r.lower)
        self.assertEqual(5, r.upper)
        self.assertTrue(r.in_range(3))
        self.assertTrue(r.in_range(2))
        self.assertTrue(r.in_range(5))
        self.assertFalse(r.in_range(6))
        self.assertFalse(r.in_range(1))

    def test_str_only_upper(self):
        r = Range("-5")
        self.assertIsNone(r.lower)
        self.assertEqual(5, r.upper)
        self.assertTrue(r.in_range(1))
        self.assertFalse(r.in_range(6))

    def test_str_integer(self):
        r = Range("3")
        self.assertIsNone(r.upper)
        self.assertEqual(3, r.lower)
        self.assertFalse(r.in_range(1))
        self.assertTrue(r.in_range(6))

    def test_str_only_lower(self):
        r = Range("2-")
        self.assertEqual(2, r.lower)
        self.assertIsNone(r.upper)
        self.assertFalse(r.in_range(1))
        self.assertTrue(r.in_range(2))
        self.assertTrue(r.in_range(6))

    def test_str_invalid(self):
        with self.assertRaises(ValueError):
            Range("-")

        with self.assertRaises(ValueError):
            Range("asdf-5")


if __name__ == "__main__":
    unittest.main()
