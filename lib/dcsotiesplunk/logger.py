# Copyright (c) 2020, DCSO GmbH

import logging
from logging import handlers
from typing import Optional
import time
import os
import sys
import json
import traceback
from collections import OrderedDict

_SPLUNK_HOME_ENV = 'SPLUNK_HOME'
_SPLUNK_LOGS = 'var/log/splunk/'  # relative to SPLUNK_HOME; never starts with /
_DCSO_TIE_LOGFILE = 'dcso_tie.log'


class UTCFormatter(logging.Formatter):
    default_time_format = '%Y-%m-%dT%H:%M:%S.uuuZ'
    converter = time.gmtime

    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        """

        :param record: a LogRecord instance
        :param datefmt: this format is ignored
        :return: RFC 3339 string, for example 2020-05-28T07:24:30.721Z
        """
        ct = self.converter(record.created)
        # we do not use the self.default_msec_format attribute
        return time.strftime(self.default_time_format, ct).replace(".uuu", ".{:03.0f}".format(record.msecs))


class UTCJSONFormatter(UTCFormatter):
    def formatException(self, ei) -> list:
        return [l for l in traceback.TracebackException(
                type(ei[1]), ei[1], ei[2], limit=None).format(chain=True)]


    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()

        rec = OrderedDict([
            ("time", self.formatTime(record, self.datefmt)),
            ("level", record.levelname),
            ("name", record.name),
            ("message", record.message),
        ])

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                rec["exceptionInfo"] = self.formatException(record.exc_info)

        if record.stack_info:
            rec["stackInfo"] = self.formatStack(record.stack_info)

        return json.dumps(rec)


def get_logger(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("dcso.tie.splunk")
    logger.propagate = False

    if hasattr(logger, 'initialized'):
        return logger

    try:
        logger.setLevel(level)
    except TypeError:
        # invalid level, we use default logging.INFO
        logger.setLevel(logging.INFO)

    fmtText = '%(asctime)s %(levelname)s [%(name)s] %(message)s'

    formatter = UTCFormatter(fmt=fmtText)
    splunk_home = os.getenv(_SPLUNK_HOME_ENV, None)

    if splunk_home:
        formatter = UTCJSONFormatter(fmt=fmtText)  # although format is not use, pass a long anyway
        f = os.path.join(splunk_home, _SPLUNK_LOGS, _DCSO_TIE_LOGFILE)
        handler = handlers.RotatingFileHandler(f, mode='a', maxBytes=10000000, backupCount=6)
        handler.setFormatter(formatter)
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)

    if handler:
        logger.addHandler(handler)

    setattr(logger, 'initialized', True)
    return logger
