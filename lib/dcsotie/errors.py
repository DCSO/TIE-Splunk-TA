# Copyright (c) 2020, 2023, DCSO GmbH


class TIEError(Exception):
    pass


class TIEConnectionError(TIEError):
    pass


class TIEAPIError(TIEError):
    pass


class TIEConfigError(TIEError):
    pass
