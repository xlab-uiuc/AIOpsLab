# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
from aiopslab.utils.actions import get_actions


class TestGetActions(unittest.TestCase):
    def test_get_actions(self):
        actions = get_actions("detection")
        expected = {
            "get_logs",
            "get_metrics",
            "get_traces",
            "read_metrics",
            "read_traces",
            "exec_shell",
            "submit",
        }
        self.assertEqual(len(actions), len(expected))
        self.assertEqual(
            set(actions.keys()),
            expected,
        )

    def test_get_read_actions(self):
        actions = get_actions("detection", "read")
        expected = {
            "get_logs",
            "get_metrics",
            "get_traces",
            "read_metrics",
            "read_traces",
        }

        self.assertEqual(len(actions), len(expected))
        self.assertEqual(
            set(actions.keys()),
            expected,
        )

    def test_get_write_actions(self):
        actions = get_actions("detection", "write")
        self.assertEqual(len(actions), 0)


if __name__ == "__main__":
    unittest.main()
