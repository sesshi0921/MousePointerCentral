import unittest

from mouse_mcp.actions import validate_actions


class ActionsTest(unittest.TestCase):
    def test_validate_actions_accept_and_reject(self):
        accepted, rejected = validate_actions(
            [
                {"type": "move", "to": [10, 20]},
                {"type": "click", "at": [10000, 1]},
                {"type": "wait", "seconds": 0.1},
            ],
            width=1920,
            height=1080,
        )
        self.assertEqual(2, len(accepted))
        self.assertEqual(1, len(rejected))


if __name__ == "__main__":
    unittest.main()
