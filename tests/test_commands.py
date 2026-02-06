#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Юнит-тесты для модуля commands.
Запуск: python -m unittest tests.test_commands
"""

import unittest
import tempfile
from pathlib import Path

from pythondocker.commands import Commands


class TestFormatSize(unittest.TestCase):
    """Тесты format_size()."""

    def setUp(self):
        self.cmd = Commands()

    def test_bytes(self):
        self.assertEqual(self.cmd.format_size(100), '100.0 B')

    def test_kb(self):
        result = self.cmd.format_size(2048)
        self.assertIn('KB', result)

    def test_mb(self):
        result = self.cmd.format_size(2 * 1024 * 1024)
        self.assertIn('MB', result)


class TestGetDirSize(unittest.TestCase):
    """Тесты _get_dir_size()."""

    def setUp(self):
        self.cmd = Commands()

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            size = self.cmd._get_dir_size(Path(tmp))
            self.assertEqual(size, 0)

    def test_dir_with_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / 'test.txt'
            f.write_text('hello')
            size = self.cmd._get_dir_size(Path(tmp))
            self.assertGreaterEqual(size, 5)


class TestInfo(unittest.TestCase):
    """Тесты info()."""

    def test_info_returns_dict(self):
        cmd = Commands()
        result = cmd.info()
        self.assertIsInstance(result, dict)
        self.assertIn('python_versions', result)
        self.assertIn('environments', result)
        self.assertIn('python_dir', result)
        self.assertIn('envs_dir', result)
        self.assertIn('pyenv_available', result)


if __name__ == '__main__':
    unittest.main()
