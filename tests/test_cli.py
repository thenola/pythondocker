#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Юнит-тесты для CLI (pythondocker.cli).
Запуск: python -m unittest tests.test_cli
"""

import unittest
import sys
from io import StringIO
from unittest.mock import patch

from pythondocker import cli


class TestCliVersion(unittest.TestCase):
    """Тесты вывода версии."""

    def test_version_flag_output(self):
        with patch.object(sys, 'argv', ['pythondocker', '--version']):
            with patch('sys.stdout', new_callable=StringIO) as out:
                cli.main()  # возвращает без exit при --version
                output = out.getvalue()
                self.assertIn('PythonDocker', output)
                self.assertIn('thenola', output)


class TestCliHelp(unittest.TestCase):
    """Тесты справки."""

    def test_help_contains_docker(self):
        with patch.object(sys, 'argv', ['pythondocker', '--help']):
            with patch('sys.stdout', new_callable=StringIO) as out:
                try:
                    cli.main()
                except SystemExit:
                    pass
                output = out.getvalue()
                self.assertIn('--docker', output)


if __name__ == '__main__':
    unittest.main()
