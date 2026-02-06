#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Юнит-тесты для модуля alternative_interpreters.
Запуск: python -m unittest tests.test_alternative_interpreters
"""

import unittest
from pythondocker import alternative_interpreters
from pythondocker.version_detector import PythonVersionDetector


class TestIsAlternativeInterpreter(unittest.TestCase):
    """Тесты is_alternative_interpreter()."""

    def test_pypy3_11(self):
        self.assertEqual(alternative_interpreters.is_alternative_interpreter('pypy3.11'), 'pypy')

    def test_pypy2_7(self):
        self.assertEqual(alternative_interpreters.is_alternative_interpreter('pypy2.7'), 'pypy')

    def test_pypy_lowercase(self):
        self.assertEqual(alternative_interpreters.is_alternative_interpreter('pypy'), 'pypy')

    def test_pypy_mixed_case(self):
        self.assertEqual(alternative_interpreters.is_alternative_interpreter('PyPy3.11'), 'pypy')

    def test_jython(self):
        self.assertEqual(alternative_interpreters.is_alternative_interpreter('jython'), 'jython')

    def test_jython2_7(self):
        self.assertEqual(alternative_interpreters.is_alternative_interpreter('jython2.7'), 'jython')

    def test_cpython_3_11(self):
        self.assertIsNone(alternative_interpreters.is_alternative_interpreter('3.11'))

    def test_cpython_2_7(self):
        self.assertIsNone(alternative_interpreters.is_alternative_interpreter('2.7'))

    def test_empty_strip(self):
        self.assertEqual(alternative_interpreters.is_alternative_interpreter('  pypy3.11  '), 'pypy')


class TestJavaAvailable(unittest.TestCase):
    """Тесты java_available()."""

    def test_returns_bool(self):
        result = alternative_interpreters.java_available()
        self.assertIsInstance(result, bool)


class TestNormalizeVersion(unittest.TestCase):
    """Тесты normalize_version() для альтернативных интерпретаторов."""

    def setUp(self):
        self.detector = PythonVersionDetector()

    def test_pypy3_11(self):
        self.assertEqual(self.detector.normalize_version('pypy3.11'), 'pypy3.11')

    def test_pypy3_10(self):
        self.assertEqual(self.detector.normalize_version('pypy3.10'), 'pypy3.10')

    def test_pypy2_7(self):
        self.assertEqual(self.detector.normalize_version('pypy2.7'), 'pypy2.7')

    def test_pypy_short(self):
        self.assertEqual(self.detector.normalize_version('pypy'), 'pypy3.11')

    def test_jython(self):
        self.assertEqual(self.detector.normalize_version('jython'), 'jython2.7')

    def test_jython2_7(self):
        self.assertEqual(self.detector.normalize_version('jython2.7'), 'jython2.7')

    def test_cpython_3_11(self):
        self.assertEqual(self.detector.normalize_version('3.11'), '3.11')

    def test_cpython_2_7(self):
        self.assertEqual(self.detector.normalize_version('2.7'), '2.7')


class TestGetPyPyUrl(unittest.TestCase):
    """Тесты get_pypy_url()."""

    def test_pypy3_11_returns_url(self):
        url = alternative_interpreters.get_pypy_url('pypy3.11')
        self.assertIsNotNone(url)
        self.assertIn('downloads.python.org', url)
        self.assertIn('pypy3.11', url)

    def test_pypy2_7_returns_url(self):
        url = alternative_interpreters.get_pypy_url('pypy2.7')
        self.assertIsNotNone(url)
        self.assertIn('pypy2.7', url)

    def test_unknown_version_returns_none(self):
        url = alternative_interpreters.get_pypy_url('pypy1.0')
        self.assertIsNone(url)


class TestConstants(unittest.TestCase):
    """Тесты констант модуля."""

    def test_pypy_releases_keys(self):
        expected = {'pypy3.11', 'pypy3.10', 'pypy3.9', 'pypy2.7'}
        self.assertEqual(set(alternative_interpreters.PYPY_RELEASES.keys()), expected)

    def test_jython_url(self):
        url = alternative_interpreters.JYTHON_URL
        self.assertIn('jython-standalone', url)
        self.assertTrue(url.endswith('.jar'))


if __name__ == '__main__':
    unittest.main()
