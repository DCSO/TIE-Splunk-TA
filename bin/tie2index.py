# Copyright (c) 2017, 2023, DCSO GmbH

from typing import Optional, NoReturn
import datetime
import sys
import os

# we change the path so that this app can run within the Splunk environment
try:
    import dcsotie
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from dcsotie.errors import TIEError, TIEConfigError
from dcsotie.fetchers import IoCFetcher
from dcsotiesplunk.config import normalize_configuration, default_configuration
from dcsotiesplunk.logger import get_logger
from dcsotiesplunk.filtering import filter_iocs

logger = get_logger().getChild("tie2index")

FIRST_RUN_TIMEDELTA = datetime.timedelta(days=30)
TIMEOUT = (3, 120)  # (connection timeout, read timeout) in seconds (can be float)
SETUP = default_configuration()

try:
    # this will only work when application is run within Splunk
    from splunk.clilib import cli_common as cli

    tie_args = cli.getConfStanza("dcso_tie_setup", "tie")
    filter_args = cli.getConfStanza("dcso_tie_setup", "filter")
    proxy_args = cli.getConfStanza("dcso_tie_setup", "proxy")

    for k, v in tie_args.items():
        SETUP["tie"][k] = v

    for k, v in filter_args.items():
        SETUP["filter"][k] = v

    for k, v in proxy_args.items():
        SETUP["proxy"][k] = v

    try:
        SETUP = normalize_configuration(SETUP)
    except TIEConfigError as local_exc:
        logger.error("configuration error: {}".format(local_exc))
        sys.exit(1)

except ImportError:
    # this will be used when not within Splunk (for example, for testing, developing, ..)
    from dcsotiesplunk.config import read_conf_from_file

    try:
        SETUP = read_conf_from_file()
    except TIEConfigError as local_exc:
        logger.error("configuration error: {}".format(local_exc))
        sys.exit(1)

    try:
        os.mkdir(os.path.join(os.path.dirname(__file__), "..", "local"))
    except FileExistsError:
        # we made sure it exists
        pass
    except Exception as local_exc:
        logger.error("failed creating local dir ({})".format(local_exc))
        sys.exit(1)


def get_proxies() -> Optional[dict]:
    proxy_cfg = SETUP["proxy"]

    if not "host" in proxy_cfg and not isinstance(str, proxy_cfg["host"]):
        return None

    host = proxy_cfg["host"].strip()

    return {
        "https": "https://{}:{}@{}:{}".format(
            str(proxy_cfg["user"]),
            str(proxy_cfg["password"]),
            host,
            str(proxy_cfg["port"]),
        )
    }


def fetch_iocs() -> NoReturn:
    proxies = get_proxies()

    fetcher = IoCFetcher(
        client_id=SETUP["tie"]["client_id"],
        client_secret=SETUP["tie"]["client_secret"],
        api_uri=SETUP["tie"]["feed_api"],
        proxies=proxies,
        timeout=TIMEOUT,
    )

    fetcher.state_file = os.path.join(
        os.path.dirname(__file__), "../local/timestamp.json"
    )

    if (
        fetcher.state["updated_at_since"] == "0"
        or fetcher.state["updated_at_since"] == 0
    ):
        # check if we had a starting timestamp configured, and use that instead
        if (
            SETUP["tie"]["updated_at_since"] != "0"
            and SETUP["tie"]["updated_at_since"] != 0
        ):
            logger.info(
                "restart fetching IoCs that were updated since {}".format(
                    SETUP["tie"]["updated_at_since"]
                )
            )
            fetcher.state["updated_at_since"] = SETUP["tie"]["updated_at_since"]
        else:
            fetcher.state["updated_at_since"] = (
                datetime.date.today() - FIRST_RUN_TIMEDELTA
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            logger.info(
                "initial fetching of IoC starting from {}".format(
                    fetcher.state["updated_at_since"]
                )
            )
    else:
        logger.info(
            "fetching IoCs that were updated since {}".format(
                fetcher.state["updated_at_since"]
            )
        )

    i = 0
    data = fetcher.fetch(
        updated_at_since=fetcher.state["updated_at_since"],
        limit=10,
    )
    try:
        while i < 50:
            i += 1

            filter_iocs(data["iocs"], SETUP["filter"], sys.stdout)

            fetcher.store_state()
            if not fetcher.have_next:
                break

            data = fetcher.next()
    except TIEConfigError as exc:
        logger.error("configuration error fetching: {}".format(exc))
    except TIEError as exc:
        logger.error("filtering IoCs error ({})".format(exc))


def run():
    if "TIE_CLIENT_ID" in os.environ:
        SETUP["tie"]["client_id"] = os.environ["TIE_CLIENT_ID"]

    if "TIE_CLIENT_SECRET" in os.environ:
        SETUP["tie"]["client_secret"] = os.environ["TIE_CLIENT_SECRET"]

    try:
        fetch_iocs()
    except KeyboardInterrupt:
        # don't output anything so it is not considered an error
        pass
    except TIEError as exc:
        logger.error(str(exc))


if __name__ == "__main__":
    run()
