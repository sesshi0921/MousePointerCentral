"""Tests for screen_percept.server tool functions (unit-level)."""

import unittest

from screen_percept.coords import CoordSpace


class TestServerImport(unittest.TestCase):
    def test_import_server(self):
        """Server module should import without crashing."""
        from screen_percept import server  # noqa: F401

    def test_mcp_name(self):
        from screen_percept.server import mcp

        self.assertEqual(mcp.name, "screen-percept")


if __name__ == "__main__":
    unittest.main()
