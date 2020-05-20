# Copyright (c) 2017, 2020, DCSO GmbH

from typing import Optional, NoReturn
import json
import datetime
import csv
import sys
import os

# we change the path so that this app can run within the Splunk environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from dcsotie.errors import TIEError
from dcsotie.fetchers import IoCFetcher
from dcsotiesplunk.config import normalize_configuration, default_configuration
from dcsotiesplunk.logger import get_logger

logger = get_logger().getChild('tie2index')

FIRST_RUN_TIMEDELTA = datetime.timedelta(days=30)
TIMEOUT = (3, 120)  # (connection timeout, read timeout) in seconds (can be float)
SETUP = default_configuration()

try:
    # this will only work when application is run within Splunk
    from splunk.clilib import cli_common as cli

    tie_args = cli.getConfStanza('dcso_tie_setup', 'tie')
    filter_args = cli.getConfStanza('dcso_tie_setup', 'filter')
    proxy_args = cli.getConfStanza('dcso_tie_setup', 'proxy')

    for k, v in tie_args.items():
        SETUP['tie'][k] = v

    for k, v in filter_args.items():
        SETUP['filter'][k] = v

    for k, v in proxy_args.items():
        SETUP['proxy'][k] = v

    SETUP = normalize_configuration(SETUP)

except ImportError:
    # this will be used when not within Splunk (for example, for testing, developing, ..)
    from dcsotiesplunk.config import read_conf_from_file

    SETUP = read_conf_from_file()
    try:
        os.mkdir(os.path.join(os.path.dirname(__file__), "..", "local"))
    except FileExistsError:
        # we make sure it exists
        pass
    except Exception as exc:
        logger.error("failed creating local dir ({})".format(exc))
        sys.exit(1)

csv.field_size_limit(sys.maxsize)


def get_proxies() -> Optional[dict]:
    proxy_cfg = SETUP['proxy']

    if not 'host' in proxy_cfg and not isinstance(str, proxy_cfg['host']):
        return None

    host = proxy_cfg['host'].strip()

    return {
        'https': 'https://{}:{}@{}:{}'.format(str(proxy_cfg['user']), str(proxy_cfg['password']),
                                              host, str(proxy_cfg['port']))
    }


def fetch_iocs() -> NoReturn:
    proxies = get_proxies()

    fetcher = IoCFetcher(
        token=SETUP['tie']['token'],
        api_uri=SETUP['tie']['feed_api'],
        proxies=proxies,
        timeout=TIMEOUT)

    fetcher.state_file = os.path.join(os.path.dirname(__file__), '../local/seq.json')

    f = SETUP['filter']

    updated_since = None
    if fetcher.state['seq_number'] == 0:
        # check if we had a starting sequence number configured, and use that instead
        if SETUP['tie']['start_ioc_seq'] != 0:
            logger.info("restart fetching IoCs at sequence number {}".format(SETUP['tie']['start_ioc_seq']))
            fetcher.state['seq_number'] = SETUP['tie']['start_ioc_seq']
        else:
            updated_since = (datetime.date.today() - FIRST_RUN_TIMEDELTA).strftime('%Y-%m-%dT%H:%M:%SZ')
            logger.info("initial fetching of IoC starting from {}".format(updated_since))
    else:
        logger.info("fetching IoCs using sequence number {}".format(fetcher.state['seq_number']))

    i = 0
    data = fetcher.fetch(updated_since=updated_since, limit=10)
    while i < 50:
        i += 1

        iocs = data['iocs']
        for ioc in iocs:
            if (ioc['data_type'] == "IPv4" and int(ioc['max_confidence']) >= int(f['ip_confidence'])
                and int(ioc['max_severity']) >= int(f['ip_severity'])) or (
                    ioc['data_type'] == "URLVerbatim" and int(ioc['max_confidence']) >= int(
                f['url_confidence']) and int(ioc['max_severity']) >= int(f['url_severity'])) or (
                    ioc['data_type'] == "DomainName" and int(ioc['max_confidence']) >= int(
                f['dom_confidence']) and int(ioc['max_severity']) >= int(f['dom_severity'])) or (
                    int(ioc['max_confidence']) >= int(f['confidence']) and
                    int(ioc['max_severity']) >= int(f['severity'])):
                print(json.dumps(ioc), file=sys.stdout)

        fetcher.store_state()
        if not fetcher.have_next:
            break

        data = fetcher.next()


if __name__ == "__main__":
    if 'TIE_TOKEN' in os.environ:
        SETUP['tie']['token'] = os.environ['TIE_TOKEN']

    try:
        fetch_iocs()
    except KeyboardInterrupt:
        # don't output anything so it is not considered an error
        pass
    except TIEError as exc:
        logger.error(str(exc))
