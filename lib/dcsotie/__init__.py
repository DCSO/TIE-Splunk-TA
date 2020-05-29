# Copyright (c) 2020, DCSO GmbH

from typing import TypeVar, Tuple, Union
import os

TIE_API = os.getenv("TIE_API", "https://tie.dcso.de/api/v1")
TIE_TOKEN = os.getenv("TIE_TOKEN", "")

TEST_API = "http://unittest.local/api"

# ATimeout is a typing alias accepting either a int or float, or
# a 2-element long tuple consisting of ints or float.
# (Somehow using TypeVar does not work well)
ATimeout = Union[Union[int, float], Tuple[Union[int, float], Union[int, float]]]
