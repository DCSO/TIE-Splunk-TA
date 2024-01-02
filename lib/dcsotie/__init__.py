# Copyright (c) 2020, 2023, DCSO GmbH

from typing import TypeVar, Tuple, Union
import os

TIE_API = os.getenv("TIE_API", "https://api.dcso.de/tie/v1")
TIE_CLIENT_ID = os.getenv("TIE_CLIENT_ID", "")
TIE_CLIENT_SECRET = os.getenv("TIE_CLIENT_SECRET", "")

TEST_API = "http://unittest.local/api"

# ATimeout is a typing alias accepting either a int or float, or
# a 2-element long tuple consisting of ints or float.
# (Somehow using TypeVar does not work well)
ATimeout = Union[Union[int, float], Tuple[Union[int, float], Union[int, float]]]
