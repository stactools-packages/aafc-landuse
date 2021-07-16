import unittest

import stactools.aafc_landuse


class TestModule(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(stactools.aafc_landuse.__version__)
