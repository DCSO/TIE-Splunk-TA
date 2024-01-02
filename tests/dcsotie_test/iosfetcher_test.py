# Copyright (c) 2020, 2023, DCSO GmbH

from datetime import datetime, timezone, timedelta
import json
import os
import requests_mock
import sys
import tempfile
import unittest

try:
    import dcsotie
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from dcsotie.fetchers import IoCFetcher
from dcsotie.errors import TIEConnectionError
from dcsotie import TIE_API

RESULT = {
    "iocs": [
        {
            "updated_at": "2023-11-30T23:44:09Z",
        },
        {
            "updated_at": "2023-11-30T23:44:09Z",
        },
        {
            "updated_at": "2023-11-30T23:45:27Z",
        },
        {
            "updated_at": "2023-11-30T23:45:27Z",
        },
        {
            "updated_at": "2023-11-30T23:46:06Z",
        },
        {
            "updated_at": "2023-11-30T23:46:06Z",
        },
        {
            "updated_at": "2023-11-30T23:47:31Z",
        },
        {
            "updated_at": "2023-11-30T23:47:31Z",
        },
        {
            "updated_at": "2023-11-30T23:48:48Z",
        },
        {
            "updated_at": "2023-11-30T23:48:48Z",
        },
    ],
    "has_more": True,
    "params": {
        "limit": 10,
    },
}


class TestIOCFetcher(unittest.TestCase):
    tmp_dir = None

    @classmethod
    def setUpClass(cls) -> None:
        if not cls.tmp_dir:
            cls.tmp_dir = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.tmp_dir:
            cls.tmp_dir.cleanup()

    def test_init(self):
        f = IoCFetcher(
            api_uri="http://localhost.local:8080",
            client_id="myclientid",
            client_secret="myclientsecret",
        )
        self.assertEqual("bXljbGllbnRpZDpteWNsaWVudHNlY3JldA==", f.token)
        self.assertEqual("http://localhost.local:8080", f.api_uri)

    def test_fetch_bad_sequence_or_limit(self):
        f = IoCFetcher(
            api_uri="http://localhost.local:8080",
            client_id="myclientid",
            client_secret="myclientsecret",
        )

        with self.assertRaises(ValueError) as ctx:
            f.fetch(updated_at_since="not a datetime")
        self.assertTrue(
            "updated_at_since must be of type datetime" in str(ctx.exception)
        )

        with self.assertRaises(ValueError) as ctx:
            f.fetch(updated_at_since="2006-01-02")
        self.assertTrue(
            "updated_at_since must be of type datetime" in str(ctx.exception)
        )

        with self.assertRaises(ValueError) as ctx:
            f.fetch(updated_at_since=datetime.now(), limit="not a number")
        self.assertTrue("limit must be number >= 0" in str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            f.fetch(updated_at_since=datetime.now(), limit=-1)
        self.assertTrue("limit must be number >= 0" in str(ctx.exception))

    def test_fetch_timeout(self):
        f = IoCFetcher(
            api_uri="http://localhost.local:8080",
            client_id="myclientid",
            client_secret="myclientsecret",
            timeout=0.02,
        )
        self.assertEqual(0.02, f.timeout)

        f = IoCFetcher(
            api_uri="http://localhost.local:8080",
            client_id="myclientid",
            client_secret="myclientsecret",
            timeout=(1, 39.9),
        )
        self.assertEqual((1, 39.9), f.timeout)

    def test_fetch_cnx_error(self):
        f = IoCFetcher(
            api_uri="http://localhost.local:8080",
            client_id="myclientid",
            client_secret="myclientsecret",
            timeout=(1, 3),
        )
        with self.assertRaises(TIEConnectionError) as ctx:
            f.fetch()
        self.assertTrue("failed connecting with TIEngine" in str(ctx.exception))

    def test_fetch(self):
        f = IoCFetcher(timeout=10)
        f.state_file = os.path.join(self.tmp_dir.name, "ioc_fetch_test.json")
        with requests_mock.Mocker() as m:
            m.register_uri(
                "GET",
                f"{TIE_API}/iocs",
                json=RESULT,
                headers={"link": f"<{TIE_API}/iocs>; rel=next"},
            )
            res = f.fetch(limit=10)
            f.store_state()

            self.assertEqual(10, len(res["iocs"]))
            self.assertEqual(10, res["params"]["limit"])
            self.assertTrue(res["has_more"])
            self.assertTrue(f.have_next)
            seqs_first = sorted([ioc["updated_at"] for ioc in res["iocs"]])

            with open(f.state_file, "r") as fp:
                state = json.load(fp)
                self.assertEqual(
                    f.state["updated_at_since"], state["tie"]["updated_at_since"]
                )

            res = f.next()
            self.assertEqual(10, len(res["iocs"]))
            self.assertEqual(10, res["params"]["limit"])
            self.assertTrue(res["has_more"])
            seqs_second = sorted([ioc["updated_at"] for ioc in res["iocs"]])

            # first of next must be higher than last of initial fetch
            # self.assertTrue(seqs_first[-1] < seqs_second[0])

            res = f.next()
            seqs_third = sorted([ioc["updated_at"] for ioc in res["iocs"]])
            # self.assertTrue(seqs_second[-1] < seqs_third[0])

    def test_fetch_using_updated_since(self):
        f = IoCFetcher(timeout=20)
        f.state_file = os.path.join(
            self.tmp_dir.name, "ioc_fetch_test_updated_since.json"
        )
        updated_since = datetime.now(timezone.utc) - timedelta(days=30)

        with requests_mock.Mocker() as m:
            m.register_uri("GET", f"{TIE_API}/iocs", json=RESULT)
            res = f.fetch(updated_at_since=updated_since, limit=10)
        f.store_state()

        self.assertEqual(10, len(res["iocs"]))
        self.assertEqual(10, res["params"]["limit"])
        self.assertTrue(res["has_more"])

        with open(f.state_file, "r") as fp:
            state = json.load(fp)
            self.assertEqual(
                f.state["updated_at_since"], state["tie"]["updated_at_since"]
            )

    def test_store_state(self):
        f = IoCFetcher(timeout=10)
        f.state_file = os.path.join(self.tmp_dir.name, "iocs_store_state.json")
        f.store_state()

        with open(f.state_file, "r") as fp:
            state = json.load(fp)

        self.assertEqual(f.state["updated_at_since"], state["tie"]["updated_at_since"])


if __name__ == "__main__":
    unittest.main()
