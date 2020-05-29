# Copyright (c) 2020, DCSO GmbH

from typing import Dict, Optional, NoReturn

from requests.utils import parse_header_links


class APIRelationshipLinks:
    relationships = ['first', 'last', 'next', 'previous']

    def __init__(self, header: str):
        self.first: Optional[str] = None
        self.last: Optional[str] = None
        self.next: Optional[str] = None
        self.previous: Optional[str] = None
        self._parse(header)

    def _parse(self, header: str):
        if not header or not isinstance(header, str):
            return

        header = header.strip()

        links = parse_header_links(header)
        for link in links:
            try:
                rel = link['rel']
                url = link['url']
            except KeyError:
                # ignore links not having relationship and url
                continue
            else:
                try:
                    self.__dict__[rel] = url
                except KeyError:
                    # ignore links we do not support
                    continue

    def as_dict(self) -> Dict:
        result = {}
        for rel in APIRelationshipLinks.relationships:
            result[rel] = getattr(self, rel, None)

        return result
