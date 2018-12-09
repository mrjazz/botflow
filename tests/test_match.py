import logging
from unittest import TestCase

logging.basicConfig(level=logging.DEBUG)


class Test:

    def __init__(self):
        pass

    def test(self):
        """
        regexp: some description
        """
        pass


class MatchTestCase(TestCase):

    def test_docs(self):
        t = Test()
        self.assertEqual("regexp: some description", t.test.__doc__.strip())
