# Copyright (c) 2020, 2023, DCSO GmbH

import os
import sys
import unittest

try:
    import dcsotie
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

if __name__ == "__main__":
    suite = unittest.TestLoader().discover(".", pattern="*_test.py")
    unittest.TextTestRunner(verbosity=2).run(suite)
