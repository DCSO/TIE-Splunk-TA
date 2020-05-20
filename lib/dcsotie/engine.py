# Copyright (c) 2020, DCSO GmbH

import json
import sys
from typing import Optional, Union, Tuple
from urllib.parse import urlparse

from . import TIE_API, TIE_TOKEN, ATimeout

REQUEST_TIMEOUT = (2, 20)

_TIE_FILE_INIT_STATE = {
    'seq_number': 0,
}


class TIEngine:
    def __init__(self, token: str = TIE_TOKEN,
                 api_uri: str = TIE_API,
                 proxies: Optional[dict] = None,
                 timeout: ATimeout = REQUEST_TIMEOUT):
        """

        :param api_uri: URI of the DCSO TIEngine
        :param token: API Token
        :param proxies: mapping of proxies
        :param timeout: request timeout in seconds (as float)
        """
        try:
            if not api_uri:
                raise ValueError
            urlparse(api_uri)
        except (AttributeError, ValueError):
            raise ValueError("API URI is invalid")

        self.token: str = token
        self.api_uri: str = api_uri.rstrip('/')
        self.proxies: Optional[dict] = None
        self.timeout: ATimeout = timeout

        self._state_file: Optional[str] = None
        self.state: dict = _TIE_FILE_INIT_STATE

    @property
    def state_file(self) -> str:
        return self._state_file

    @state_file.setter
    def state_file(self, path):
        self._state_file = path
        try:
            with open(self._state_file, 'r') as fp:
                data = json.load(fp)
                self.state = data['tie']
        except FileNotFoundError:
            # not having the file is OK
            pass
        except (ValueError, KeyError):
            print("WARNING: state file not something usable", file=sys.stderr)
            self.state = _TIE_FILE_INIT_STATE

    def store_state(self):
        if not self._state_file:
            return

        payload = {
            'tie': self.state
        }

        with open(self._state_file, 'w') as fp:
            json.dump(payload, fp)
            fp.write("\n")  # be nice
