# Copyright (c) 2020, DCSO GmbH

import logging
from logging import handlers
import os
import sys

_SPLUNK_HOME_ENV = 'SPLUNK_HOME'
_SPLUNK_LOGS = 'var/log/splunk/'  # relative to SPLUNK_HOME; never starts with /
_DCSO_TIE_LOGFILE = 'dcso_tie.log'


def get_logger(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("dcso.tie.splunk")
    logger.propagate = False

    try:
        logger.setLevel(level)
    except TypeError:
        # invalid level, we use default logging.INFO
        logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s')

    splunk_home = os.getenv(_SPLUNK_HOME_ENV, None)

    if splunk_home:
        f = os.path.join(splunk_home, _SPLUNK_LOGS, _DCSO_TIE_LOGFILE)
        handler = handlers.RotatingFileHandler(f, mode='a', maxBytes=10000000, backupCount=6)
        handler.setFormatter(formatter)
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)

    if handler:
        logger.addHandler(handler)

    return logger
