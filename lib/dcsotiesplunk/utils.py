# Copyright (c) 2020, DCSO GmbH

import sys


def print_error(msg: str):
    print("ERROR: {}".format(msg), file=sys.stderr)


def print_info(msg: str):
    print("INFO: {}".format(msg), file=sys.stderr)
