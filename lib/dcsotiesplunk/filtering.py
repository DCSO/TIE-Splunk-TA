# Copyright (c) 2017, 2020, DCSO GmbH

import json
import sys
import os

# we change the path so that this app can run within the Splunk environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from dcsotie.errors import TIEError
from dcsotiesplunk.logger import get_logger

logger = get_logger().getChild('.filtering')

DATA_TYPE_FILTER_MAP = {
    'IPv4': 'ip',
    'URLVerbatim': 'url',
    'DomainName': 'dom',
}


def filter_iocs(iocs, filters, fp=sys.stdout):
    tmpl_filters = {
        'confidence': None,
        'max_severity': None
    }
    filter_cache = {}

    for ioc in iocs:
        try:
            max_confidence = int(ioc['max_confidence'])
        except (TypeError, ValueError):
            logger.error("bad value for max_confidence; was {}".format(ioc['max_confidence']))
            continue

        try:
            max_severity = int(ioc['max_severity'])
        except (TypeError, ValueError):
            logger.error("bad value for max_severity; was {}".format(ioc['max_severity']))
            continue

        dt = ioc['data_type']
        try:
            f = filter_cache[dt]
        except KeyError:
            # warm up
            f = filter_cache[dt] = tmpl_filters.copy()
            try:
                p = DATA_TYPE_FILTER_MAP[ioc['data_type']]
                f['confidence'] = filters[p + '_confidence']
                f['max_severity'] = filters[p + '_severity']
            except KeyError:
                f['confidence'] = filters['confidence']
                f['max_severity'] = filters['severity']

        try:
            if (f['confidence'].in_range(max_confidence)
                    and f['max_severity'].in_range(max_severity)):
                print(json.dumps(ioc), file=fp)
        except AttributeError as exc:
            raise TIEError(str(exc))
