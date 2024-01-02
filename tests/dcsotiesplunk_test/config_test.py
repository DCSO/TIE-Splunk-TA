# Copyright (c) 2020, 2023, DCSO GmbH

import os
import sys
import unittest

try:
    import dcsotie
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from dcsotiesplunk.config import (
    normalize_configuration,
    CONFIG_SCHEMA,
    default_configuration,
)
from dcsotie.utils import SeverityRange
from dcsotie.errors import TIEConfigError


TEST_LINK_HEADER = """
<https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=60>; rel=previous, <https://api.dcso.de/tie/api/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=100>; rel=next, <https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=680>; rel=last, <https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=0>; rel=first
"""

TEST_LINK_HEADER_EXP = {
    "first": "https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=0",
    "last": "https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=680",
    "next": "https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=100",
    "previous": "https://api.dcso.de/tie/v1/raw_iocs?limit=20&data_type=domainname%2Cipv4&offset=60",
}


class TestNormalizeConfig(unittest.TestCase):
    def test_normalize(self):
        have = default_configuration()
        have["filter"]["url_severity"] = "3"

        res = normalize_configuration(have)
        self.assertIsInstance(res["filter"]["url_severity"], SeverityRange)

        exp = CONFIG_SCHEMA["filter"]["url_severity"][0](have["filter"]["url_severity"])
        self.assertEqual(
            exp,
            res["filter"]["url_severity"],
            msg="Range {} != Range {}".format(exp, res["filter"]["url_severity"]),
        )

        self.assertEqual(CONFIG_SCHEMA["tie"]["feed_api"][1], res["tie"]["feed_api"])

    def test_wrong_value_severity(self):
        have = default_configuration()
        have["filter"]["url_severity"] = "3-foobar"

        with self.assertRaises(TIEConfigError) as ctx:
            normalize_configuration(have)

        self.assertEqual("range string not valid; was 3-foobar", str(ctx.exception))


class TestDefaultConf(unittest.TestCase):
    def test_default(self):
        res = default_configuration()

        exp = CONFIG_SCHEMA["filter"]["dom_confidence"][0](
            CONFIG_SCHEMA["filter"]["dom_confidence"][1]
        )
        self.assertEqual(exp, res["filter"]["dom_confidence"])
        self.assertEqual(CONFIG_SCHEMA["tie"]["feed_api"][1], res["tie"]["feed_api"])


if __name__ == "__main__":
    unittest.main()
