import unittest

from mouse_mcp import server


class ExecuteDryRunTest(unittest.TestCase):
    def test_execute_dry_run_smoke(self):
        server.clear_queue()
        server.enqueue_actions(
            [
                {"type": "move", "to": [100, 100]},
                {"type": "wait", "seconds": 0.01},
                {"type": "click", "at": [100, 100]},
            ]
        )
        result = server.execute(record=False, dry_run=True)
        self.assertEqual("completed", result["status"])
        self.assertGreaterEqual(len(result["log"]), 3)


if __name__ == "__main__":
    unittest.main()
