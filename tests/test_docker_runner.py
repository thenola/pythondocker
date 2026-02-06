#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Юнит-тесты для модуля docker_runner.
Запуск: python -m unittest tests.test_docker_runner
"""

import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from pythondocker.docker_runner import (
    DOCKER_IMAGES,
    get_docker_image,
    _path_for_docker,
    docker_available,
)


class TestGetDockerImage(unittest.TestCase):
    """Тесты get_docker_image()."""

    def test_cpython_27(self):
        self.assertEqual(get_docker_image('2.7'), 'python:2.7-slim')

    def test_cpython_311(self):
        self.assertEqual(get_docker_image('3.11'), 'python:3.11-slim')

    def test_cpython_311_5(self):
        self.assertEqual(get_docker_image('3.11.5'), 'python:3.11-slim')

    def test_pypy311(self):
        self.assertEqual(get_docker_image('pypy3.11'), 'pypy:3.11-slim')

    def test_pypy27(self):
        self.assertEqual(get_docker_image('pypy2.7'), 'pypy:2.7-slim')

    def test_pypy_unknown(self):
        result = get_docker_image('pypy1.0')
        self.assertIsNone(result)

    def test_jython_returns_none(self):
        result = get_docker_image('jython')
        self.assertIsNone(result)


class TestPathForDocker(unittest.TestCase):
    """Тесты _path_for_docker()."""

    def test_unix_path_unchanged(self):
        p = Path('/home/user/project')
        result = _path_for_docker(p)
        self.assertIn('/home/user/project', result)
        self.assertNotIn('\\', result)

    @unittest.skipIf(
        __import__('sys').platform != 'win32',
        'Windows path conversion only on Windows'
    )
    def test_windows_path_conversion(self):
        p = Path('C:/Users/test/project')
        result = _path_for_docker(p)
        # Docker Desktop принимает C:/path (forward slashes)
        self.assertIn('C:/', result)
        self.assertNotIn('\\', result)


class TestDockerAvailable(unittest.TestCase):
    """Тесты docker_available()."""

    def test_returns_bool(self):
        result = docker_available()
        self.assertIsInstance(result, bool)

    @patch('pythondocker.docker_runner.subprocess.run')
    def test_returns_true_when_docker_ok(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = docker_available()
        self.assertTrue(result)
        mock_run.assert_called_once()


class TestDockerImagesConstant(unittest.TestCase):
    """Тесты константы DOCKER_IMAGES."""

    def test_has_cpython(self):
        self.assertIn('2.7', DOCKER_IMAGES)
        self.assertIn('3.11', DOCKER_IMAGES)

    def test_has_pypy(self):
        self.assertIn('pypy3.11', DOCKER_IMAGES)
        self.assertIn('pypy2.7', DOCKER_IMAGES)

    def test_images_contain_slim(self):
        for img in DOCKER_IMAGES.values():
            self.assertIn('slim', img)


if __name__ == '__main__':
    unittest.main()
