# Perceptual image hash calculation tool based on algorithm descibed in
# Block Mean Value Based Image Perceptual Hashing by Bian Yang, Fan Gu and Xiamu Niu
#
# Copyright 2014 Commons Machinery http://commonsmachinery.se/
# Distributed under an MIT license, please see LICENSE in the top dir.

import unittest
import os
import glob

import PIL.Image as Image

import blockhash.core

datadir = os.path.join(os.path.dirname(__file__), 'data')

class BlockhashTestCase(unittest.TestCase):
    def __init__(self, img_filename=None, hash_filename=None, method=None, bits=None):
        unittest.TestCase.__init__(self)
        self.img_filename = img_filename
        self.hash_filename = hash_filename
        self.method = method
        self.bits = bits

    def runTest(self):
        im = Image.open(self.img_filename)

        # convert indexed/grayscale images to RGB
        if im.mode == '1' or im.mode == 'L' or im.mode == 'P':
            im = im.convert('RGB')
        elif im.mode == 'LA':
            im = im.convert('RGBA')

        with open(self.hash_filename) as f:
            expected_hash = f.readline().split()[0]

            if self.method == 1:
                method = blockhash.core.blockhash_even
            elif self.method == 2:
                method = blockhash.core.blockhash

            hash = method(im, self.bits)
            hash = "".join([str(x) for x in hash])
            self.assertEqual(expected_hash, hash)

def load_tests(loader, tests, pattern):
    test_cases = unittest.TestSuite()
    for img_fn in (glob.glob(os.path.join(datadir, '*.jpg')) +
                   glob.glob(os.path.join(datadir, '*.png'))):
        for m in range(2):
            bits = 16
            method = m + 1
            basename, ext = os.path.splitext(img_fn)
            hash_fn = basename + '_{}_{}.txt'.format(bits, method)
            test_cases.addTest(BlockhashTestCase(img_fn, hash_fn, method, bits))
        pass
    return test_cases


class TestBlockhash(unittest.TestCase):
    def test_blockhash_even(self):
        filepath = os.path.join(_ASSETS_PATH, 'swiss_army_knife.jpg')

        with Image.open(filepath) as im:
            digest = blockhash.core.blockhash_even(im, 16)

        self.assertEquals(digest, 'ffcff903f801e800ff01fc03fc03f803e00fc20fe00ff1cff00ff01ffc1ffe7f')

    def test_blockhash(self):
        filepath = os.path.join(_ASSETS_PATH, 'swiss_army_knife.jpg')

        with Image.open(filepath) as im:
            digest = blockhash.core.blockhash(im, 16)

        self.assertEquals(digest, 'ff4ff907f801e800ff01fc83fc03f003e00fc20fe00ff1cff00ff81ffc1ffe7f')
