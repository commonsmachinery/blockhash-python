import unittest
import os

import PIL.Image as Image

import blockhash.blockhash

_ASSETS_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets')


class TestBlockhash(unittest.TestCase):
    def test_blockhash_even(self):
        filepath = os.path.join(_ASSETS_PATH, 'swiss_army_knife.jpg')

        with Image.open(filepath) as im:
            digest = blockhash.blockhash.blockhash_even(im, 16)

        self.assertEquals(digest, 'ffcff903f801e800ff01fc03fc03f803e00fc20fe00ff1cff00ff01ffc1ffe7f')

    def test_blockhash(self):
        filepath = os.path.join(_ASSETS_PATH, 'swiss_army_knife.jpg')

        with Image.open(filepath) as im:
            digest = blockhash.blockhash.blockhash(im, 16)

        self.assertEquals(digest, 'ff4ff907f801e800ff01fc83fc03f003e00fc20fe00ff1cff00ff81ffc1ffe7f')
