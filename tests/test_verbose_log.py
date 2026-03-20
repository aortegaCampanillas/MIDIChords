"""Tests del modo verbose (CLI / entorno)."""

from __future__ import annotations

import os
import unittest

from midichords.core import verbose_log


class VerboseLogTests(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("MIDICHORDS_VERBOSE", None)

    def test_is_verbose_off_by_default(self) -> None:
        os.environ.pop("MIDICHORDS_VERBOSE", None)
        self.assertFalse(verbose_log.is_verbose())

    def test_is_verbose_on_for_1(self) -> None:
        os.environ["MIDICHORDS_VERBOSE"] = "1"
        self.assertTrue(verbose_log.is_verbose())

    def test_is_verbose_on_for_true_case_insensitive(self) -> None:
        os.environ["MIDICHORDS_VERBOSE"] = "TRUE"
        self.assertTrue(verbose_log.is_verbose())


if __name__ == "__main__":
    unittest.main()
