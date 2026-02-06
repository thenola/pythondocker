#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Юнит-тесты для модуля pyenv_manager.
Запуск: python -m unittest tests.test_pyenv_manager
"""

import unittest
from unittest.mock import patch, MagicMock

from pythondocker.pyenv_manager import PyenvManager


class TestPyenvManager(unittest.TestCase):
    """Тесты PyenvManager."""

    def test_init_creates_attributes(self):
        mgr = PyenvManager()
        self.assertIsInstance(mgr.pyenv_available, bool)
        self.assertTrue(mgr.pyenv_root is None or mgr.pyenv_root is not None)

    @patch('subprocess.run')
    def test_version_installed_when_pyenv_unavailable(self, mock_run):
        mgr = PyenvManager()
        mgr.pyenv_available = False
        result = mgr.version_installed('3.11.0')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
