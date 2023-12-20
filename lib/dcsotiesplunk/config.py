# Copyright (c) 2020, 2023, DCSO GmbH
from configparser import ConfigParser
from typing import NoReturn, Optional, Any, Union

from dcsotie.errors import TIEConfigError
from dcsotie.utils import Range, SeverityRange, ConfidenceRange

CONFIG_SCHEMA = {
    "filter": {
        "ip_confidence": (ConfidenceRange, 80),
        "ip_severity": (SeverityRange, 1),
        "dom_confidence": (ConfidenceRange, 80),
        "dom_severity": (SeverityRange, 1),
        "url_confidence": (ConfidenceRange, 80),
        "url_severity": (SeverityRange, 1),
        "email_confidence": (ConfidenceRange, 80),
        "email_severity": (SeverityRange, 1),
        "confidence": (ConfidenceRange, 80),
        "severity": (SeverityRange, 2),
    },
    "tie": {
        "client_id": (str, ""),
        "client_secret": (str, ""),
        "feed_api": (str, "https://api.dcso.de/tie/v1/iocs"),
        "updated_at_since": (str, ""),
    },
    "proxy": {
        "host": (str, ""),
        "port": (str, ""),
        "user": (str, ""),
        "password": (str, ""),
    },
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
    :raises TIEConfigError: when configuration contains errors.
    """
    cfg = ConfigParser()

    locations = [
        "../default/dcso_tie_setup.conf",
        "default/dcso_tie_setup.conf",
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
            cfg_value = configuration[section][k]

            if issubclass(s[0], Range):
                if isinstance(cfg_value, Range):
                    # we already have a range
                    res[section].setdefault(k, cfg_value)
                else:
                    try:
                        if k.endswith("severity"):
                            res[section].setdefault(k, SeverityRange(cfg_value))
                        elif k.endswith("confidence"):
                            res[section].setdefault(k, ConfidenceRange(cfg_value))
                        else:
                            res[section].setdefault(k, Range(cfg_value))
                    except ValueError as exc:
                        raise TIEConfigError(str(exc))
            else:
                res[section].setdefault(k, s[0](cfg_value))

    return res


def default_configuration() -> dict:
    res = {}

    for section in CONFIG_SCHEMA.keys():
        if section not in res:
            res[section] = {}
        for k, s in CONFIG_SCHEMA[section].items():
            if issubclass(s[0], Range):
                res[section][k] = s[0](s[1])
            else:
                res[section][k] = s[1]

    return res


def normalize_splunk_setup_args(data: dict, labels: Optional[dict] = None) -> NoReturn:
    """
    Normalizes the data entered when setting up the Splunk app or add-on. The data
    argument is Splunk's ConfigApp.callerArgs.data attribute. It is a key/value
    mapping.

    :param data: dictionary containing configuration gathered through setup.xml
    :param labels: optional labels for the keys within data (helpful for more human readable errors)
    :raises TIEConfigError: when a value is invalid
    """

    if labels is None:
        labels = {}

    for k, v in data.items():
        label = labels.get(k, k)

        #
        # single value entries
        #
        try:
            v = v[0].strip()  # whitespace at both ends is useless
        except AttributeError:
            # if not a string, all is ok
            pass

        if k == "client_id":
            if not v:
                raise TIEConfigError("{} is required".format(label))
            data[k][0] = str(v)
        elif k == "client_secret":
            if not v:
                raise TIEConfigError("{} is required".format(label))
            data[k][0] = str(v)
        elif k == "updated_at_since":
            try:
                data[k][0] = str(v)
            except (TypeError, ValueError):
                raise TIEConfigError("invalid date string for {}".format(label))
