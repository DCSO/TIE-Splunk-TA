# Copyright (c) 2020, 2023, DCSO GmbH

from datetime import datetime
import numbers
from typing import Any, Optional, Dict

import requests

from .engine import TIEngine, REQUEST_TIMEOUT
from .errors import TIEConnectionError, TIEAPIError
from . import TIE_API, TIE_CLIENT_ID, TIE_CLIENT_SECRET
from .utils import APIRelationshipLinks
from . import ATimeout


class IoCFetcher(TIEngine):
    def __init__(
        self,
        client_id: str = TIE_CLIENT_ID,
        client_secret: str = TIE_CLIENT_SECRET,
        api_uri: str = TIE_API,
        proxies: Optional[dict] = None,
        timeout: ATimeout = REQUEST_TIMEOUT,
        raw: bool = False,
    ):
        super().__init__(
            api_uri=api_uri,
            client_id=client_id,
            client_secret=client_secret,
            timeout=timeout,
            proxies=proxies,
        )
        self.have_next: bool = False
        self.sequence: int = 0
        self.endpoint: str = self.api_uri
        if not self.endpoint.endswith("/iocs"):
            self.endpoint += "/iocs"
        self.elapsed: int = 0
        self._raw: bool = raw
        self.retry: int = 3
        self.relations: Optional[APIRelationshipLinks] = None

    def fetch(
        self,
        limit: int = 1000,
        updated_at_since: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    ) -> Any:
        """
        Fetch IoCs starting at given datetime. Limit is the number of returned entries.

        :param updated_at_since: get IoCs since given datetime
        :param limit: limit the number of returned IoCs
        :param raw: returns the raw result (JSON as bytes)
        :raises ValueError:
            When update_at_since is not a str
            When limit is not number >= 0.
        :raises TIEConnectionError: When not able to connect with TIEngine.
        """

        if not isinstance(limit, numbers.Number) or limit < 0:
            raise ValueError("limit must be number >= 0")

        if not isinstance(updated_at_since, str):
            raise ValueError("updated_at_since must be of type str")

        params = {
            "updated_at_since": updated_at_since,
            "order_by": "updated_at",
            "direction": "asc",
            "limit": limit,
        }

        return self._fetch(self.endpoint, params=params)

    def _fetch(self, uri: str, params: Optional[Dict] = None) -> Any:
        headers = {
            "Authorization": "Basic " + self.token,
            "Accept": "application/json",
        }

        resp = None
        for i in range(0, self.retry):
            try:
                resp = requests.get(
                    uri,
                    headers=headers,
                    params=params,
                    timeout=self.timeout,
                    proxies=self.proxies,
                )
            except requests.exceptions.ConnectionError:
                if i == self.retry - 1:
                    raise TIEConnectionError(
                        "failed connecting with TIEngine {}".format(self.api_uri)
                    )
                continue
            except requests.exceptions.ReadTimeout as exc:
                if i == self.retry - 1:
                    raise TIEConnectionError(
                        "failed reading from TIEngine ({})".format(str(exc))
                    )
                continue

            if resp.status_code != 200:
                if i == self.retry - 1:
                    raise TIEAPIError(
                        "failed API request; got status {}".format(resp.status_code)
                    )
                continue

            self.elapsed = resp.elapsed
            break

        if resp is None:
            raise TIEAPIError(
                "failed API request; got no response".format(resp.status_code)
            )

        try:
            self.relations = APIRelationshipLinks(resp.headers["Link"])
        except KeyError:
            self.have_next = False
        else:
            self.have_next = self.relations.next is not None

        data = resp.json()

        # store highest datetime
        if len(data["iocs"]) > 0:
            self.state["updated_at_since"] = sorted(
                [ioc["updated_at"] for ioc in data["iocs"]]
            )[-1]

        try:
            if self._raw:
                return resp.content
            return data
        except ValueError as exc:
            raise TIEAPIError("failed decoding JSON response ({})".format(exc))

    def next(self) -> Any:
        if self.relations is None or self.relations.next is None:
            return None

        return self._fetch(self.relations.next)
