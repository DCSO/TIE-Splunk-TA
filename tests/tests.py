# Copyright (c) 2020, DCSO GmbH

import os
import sys
import unittest

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

    suite = unittest.TestLoader().discover('.', pattern="*_test.py")
    unittest.TextTestRunner(verbosity=2).run(suite)
