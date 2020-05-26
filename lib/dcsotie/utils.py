# Copyright (c) 2020, DCSO GmbH

from typing import Dict, Optional, Tuple, Union
import re

from requests.utils import parse_header_links

_RE_RANGE_STR = re.compile(r'^(\d*)-(\d*)$')
ARange = Union[int, Tuple[int, int], str]


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


class Range:
    """
    Range definition
    """
    max_upper = None

    def __init__(self, r: ARange):
        self.lower = 0
        self.upper = None

        if isinstance(r, int):
            if r < 0:
                raise ValueError("range lower cannot be negative")
            self.lower = r
        elif isinstance(r, (tuple, list)):
            self.lower = r[0]
            self.upper = r[1]
        elif isinstance(r, str):
            r = r.strip()
            try:
                self.lower = int(r)
                if self.lower < 0:
                    raise ValueError("range cannot be negative")
            except (TypeError, ValueError):
                # next up is to get range syntax from string
                m = _RE_RANGE_STR.match(r)
                if m is None:
                    raise ValueError("range string not valid; was {}".format(r))
                self.lower = int(m.group(1)) if m.group(1) != '' else None
                self.upper = int(m.group(2)) if m.group(2) != '' else None
                if self.lower is None and self.upper is None:
                    raise ValueError("range not valid; was {}".format(r))
        else:
            raise ValueError("range string not valid; was {}".format(r))

        if self.__class__.max_upper is not None:
            if self.upper is None:
                self.upper = self.__class__.max_upper
            elif self.upper > self.__class__.max_upper:
                raise ValueError("range should be between 0 and {} (was {})".format(
                    self.__class__.max_upper, str(self)))

        if self.upper is not None and self.lower is not None and self.lower > self.upper:
            raise ValueError("range lower is higher than upper; was {}".format(r))

    def in_range(self, i: int) -> bool:
        if self.lower is None:
            return i <= self.upper
        if self.upper is None:
            return i >= self.lower

        return self.lower <= i <= self.upper

    def __str__(self) -> str:
        return '{}-{}'.format(
            self.lower if self.lower is not None else '',
            self.upper if self.upper is not None else '')

    def __eq__(self, other):
        return other.lower == self.lower and other.upper == self.upper


class SeverityRange(Range):
    """
    SeverityRange is a Range which lower is 0 and upper maximum 6.
    """
    max_upper = 6


class ConfidenceRange(Range):
    """
    ConfidenceRange is a Range which lower is 0 and upper maximum 100.
    """
    max_upper = 100
