import unittest
from unittest.mock import patch

from mouse_mcp.recorder import Recorder


class RecorderPlatformTest(unittest.TestCase):
    def test_platform_input_for_macos(self):
        with patch("mouse_mcp.recorder.platform.system", return_value="Darwin"):
            recorder = Recorder()
            self.assertEqual(["-f", "avfoundation", "-i", "1:none"], recorder._platform_input())

    def test_platform_input_for_windows(self):
        with patch("mouse_mcp.recorder.platform.system", return_value="Windows"):
            recorder = Recorder()
            self.assertEqual(["-f", "gdigrab", "-i", "desktop"], recorder._platform_input())

    def test_platform_input_for_linux(self):
        with patch("mouse_mcp.recorder.platform.system", return_value="Linux"):
            recorder = Recorder()
            self.assertEqual(["-f", "x11grab", "-i", ":0.0"], recorder._platform_input())


if __name__ == "__main__":
    unittest.main()
