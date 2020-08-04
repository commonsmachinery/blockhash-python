import unittest
import os
import subprocess

_APP_PATH = os.path.join(os.path.dirname(__file__), '..', '..')
_ASSETS_PATH = os.path.join(_APP_PATH, 'assets')
_SCRIPT_FILEPATH = os.path.join(_APP_PATH, 'blockhash', 'resources', 'scripts', 'blockhash')


class TestCommand(unittest.TestCase):
    def test_run__slow(self):
        filepath = os.path.join(_ASSETS_PATH, 'swiss_army_knife.jpg')

        cmd = [
            _SCRIPT_FILEPATH,
            filepath,
        ]

        output = \
            subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                universal_newlines=True)

        parts = output.split()

        self.assertEquals(parts[0], 'ff4ff907f801e800ff01fc83fc03f003e00fc20fe00ff1cff00ff81ffc1ffe7f')

    def test_run__quick(self):
        filepath = os.path.join(_ASSETS_PATH, 'swiss_army_knife.jpg')

        cmd = [
            _SCRIPT_FILEPATH,
            '--quick',
            filepath,
        ]

        output = \
            subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                universal_newlines=True)

        parts = output.split()

        self.assertEquals(parts[0], 'ffcff903f801e800ff01fc03fc03f803e00fc20fe00ff1cff00ff01ffc1ffe7f')
