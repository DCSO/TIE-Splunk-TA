# Copyright (c) 2020, DCSO GmbH

from configparser import ConfigParser
from typing import Optional, Any, Union

CONFIG_SCHEMA = {
    'filter': {
        'ip_confidence': (int, 80),
        'ip_severity': (int, 1),
        'dom_confidence': (int, 80),
        'dom_severity': (int, 1),
        'url_confidence': (int, 80),
        'url_severity': (int, 1),
        'email_confidence': (int, 80),
        'email_severity': (int, 1),
        'confidence': (int, 80),
        'severity': (int, 2),
    },
    'tie': {
        'token': (str, ''),
        'feed_api': (str, 'https://tie.dcso.de/api/v1/iocs'),
        'pingback_api': (str, 'https://pingback.dcso.de/api/v1/submit'),
        'start_ioc_seq': (int, 0),
    },
    'proxy': {
        'host': (str, ''),
        'port': (str, ''),
        'user': (str, ''),
        'password': (str, ''),
    }
}


def read_conf_from_file(file: Optional[str] = None) -> Any:
    """
    Read the TIE Splunk configuration from file. This is useful for when testing
    or developing. Returned is the configuration as mapping.

    The following files are tried to be read:
    * `default/dcso_tie_setup.conf`
    * `../default/dcso_tie_setup.conf`

    First found is read, parsed, and result returned. Others are ignored.

    :param file: file to be read
    :return: configuration as read from the configuration file.
    """
    cfg = ConfigParser()

    locations = [
        '../default/dcso_tie_setup.conf',
        'default/dcso_tie_setup.conf',
    ]

    if file:
        locations = [file]

    for l in locations:
        try:
            with open(l) as fp:
                cfg.read_file(fp)
        except FileNotFoundError:
            pass
        else:
            return normalize_configuration(cfg)


def normalize_configuration(configuration: Union[ConfigParser, dict]) -> dict:
    res = {}

    for section in CONFIG_SCHEMA.keys():
        if section not in res:
            res[section] = {}
        for k, s in CONFIG_SCHEMA[section].items():
            try:
                res[section][k] = s[0](configuration[section][k])
            except KeyError:
                res[section][k] = s[1]

    return res


def default_configuration() -> dict:
    res = {}

    for section in CONFIG_SCHEMA.keys():
        if section not in res:
            res[section] = {}
        for k, s in CONFIG_SCHEMA[section].items():
            res[section][k] = s[1]

    return res