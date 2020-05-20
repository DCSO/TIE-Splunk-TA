# Copyright (c) 2020, DCSO GmbH

from datetime import datetime, timezone, timedelta
import json
import os
import sys
import tempfile
import unittest

from dcsotie.fetchers import IoCFetcher
from dcsotie.errors import TIEConnectionError
from dcsotie import TIE_TOKEN


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
        f = IoCFetcher(api_uri='http://localhost.local:8080', token='mytoken')
        self.assertEqual('mytoken', f.token)
        self.assertEqual('http://localhost.local:8080', f.api_uri)

    def test_fetch_bad_sequence_or_limit(self):
        f = IoCFetcher(api_uri='http://localhost.local:8080', token='mytoken')

        with self.assertRaises(ValueError) as ctx:
            f.fetch(sequence="not a number")
        self.assertTrue("sequence must be number >= 0" in str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            f.fetch(sequence=-1)
        self.assertTrue("sequence must be number >= 0" in str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            f.fetch(sequence=0, limit="not a number")
        self.assertTrue("limit must be number >= 0" in str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            f.fetch(sequence=0, limit=-1)
        self.assertTrue("limit must be number >= 0" in str(ctx.exception))

    def test_fetch_timeout(self):
        f = IoCFetcher(api_uri='http://localhost.local:8080', token='mytoken', timeout=0.02)
        self.assertEqual(0.02, f.timeout)

        f = IoCFetcher(api_uri='http://localhost.local:8080', token='mytoken', timeout=(1, 39.9))
        self.assertEqual((1, 39.9), f.timeout)

    def test_fetch_cnx_error(self):
        f = IoCFetcher(api_uri='http://localhost.local:8080', token='mytoken', timeout=0.5)
        with self.assertRaises(TIEConnectionError) as ctx:
            f.fetch()
        self.assertTrue("failed connecting with TIEngine" in str(ctx.exception))

    @unittest.skipIf(TIE_TOKEN == "", "TIEngine token not available as TIE_TOKEN environment variable")
    def test_fetch(self):
        f = IoCFetcher(timeout=10)
        f.state_file = os.path.join(self.tmp_dir.name, "ioc_fetch_test.json")
        res = f.fetch(limit=10)
        f.store_state()

        self.assertEqual(10, len(res['iocs']))
        self.assertEqual(10, res['params']['limit'])
        self.assertTrue(res['has_more'])
        self.assertTrue(f.have_next)
        seqs_first = sorted([ioc['min_seq'] for ioc in res['iocs']])

        with open(f.state_file, 'r') as fp:
            state = json.load(fp)
            self.assertEqual(f.state['seq_number'], state['tie']['seq_number'])

        res = f.next()
        self.assertEqual(10, len(res['iocs']))
        self.assertEqual(10, res['params']['limit'])
        self.assertTrue(res['has_more'])
        seqs_second = sorted([ioc['min_seq'] for ioc in res['iocs']])

        # first of next must be higher than last of initial fetch
        # self.assertTrue(seqs_first[-1] < seqs_second[0])

        res = f.next()
        seqs_third = sorted([ioc['min_seq'] for ioc in res['iocs']])
        # self.assertTrue(seqs_second[-1] < seqs_third[0])

    @unittest.skipIf(TIE_TOKEN == "", "TIEngine token not available as TIE_TOKEN environment variable")
    def test_fetch_using_updated_since(self):
        f = IoCFetcher(timeout=20)
        f.state_file = os.path.join(self.tmp_dir.name, "ioc_fetch_test_updated_since.json")
        updated_since = datetime.now(timezone.utc) - timedelta(hours=1)
        res = f.fetch(updated_since=updated_since, limit=10)
        f.store_state()

        self.assertEqual(10, len(res['iocs']))
        self.assertEqual(10, res['params']['limit'])
        self.assertTrue(res['has_more'])

        with open(f.state_file, 'r') as fp:
            state = json.load(fp)
            self.assertEqual(f.state['seq_number'], state['tie']['seq_number'])

    def test_store_state(self):
        f = IoCFetcher(timeout=10)
        f.state_file = os.path.join(self.tmp_dir.name, "iocs_store_state.json")
        f.store_state()

        with open(f.state_file, 'r') as fp:
            state = json.load(fp)

        self.assertEqual(f.state['seq_number'], state['tie']['seq_number'])


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', "lib"))

    unittest.main()
