#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Юнит-тесты для модуля version_detector.
Запуск: python -m unittest tests.test_version_detector
"""

import unittest
import tempfile
from pathlib import Path

from pythondocker.version_detector import PythonVersionDetector


class TestCheckShebang(unittest.TestCase):
    """Тесты _check_shebang()."""

    def setUp(self):
        self.detector = PythonVersionDetector()

    def test_shebang_python27(self):
        self.assertEqual(self.detector._check_shebang('#!/usr/bin/env python2.7'), '2.7')

    def test_shebang_python3(self):
        self.assertEqual(self.detector._check_shebang('#!/usr/bin/env python3.11'), '3.11')

    def test_shebang_python_no_version(self):
        self.assertEqual(self.detector._check_shebang('#!/usr/bin/env python'), '3.11')

    def test_shebang_alt_format(self):
        self.assertEqual(self.detector._check_shebang('#!/usr/bin/python2.7'), '2.7')

    def test_shebang_empty(self):
        self.assertIsNone(self.detector._check_shebang(''))

    def test_shebang_not_shebang(self):
        self.assertIsNone(self.detector._check_shebang('# comment'))


class TestCheckVersionComment(unittest.TestCase):
    """Тесты _check_version_comment()."""

    def setUp(self):
        self.detector = PythonVersionDetector()

    def test_requires_python_27(self):
        self.assertEqual(self.detector._check_version_comment('# Requires Python 2.7'), '2.7')

    def test_version_comment_311(self):
        # Паттерн ожидает "python" сразу перед цифрами: # ... python 3.11
        self.assertEqual(self.detector._check_version_comment('# Python 3.11'), '3.11')

    def test_no_version(self):
        self.assertIsNone(self.detector._check_version_comment('# обычный комментарий'))


class TestCheckSyntax(unittest.TestCase):
    """Тесты _check_syntax()."""

    def setUp(self):
        self.detector = PythonVersionDetector()

    def test_python2_syntax_detected(self):
        content = 'print "hello"\nfor i in xrange(5): pass'
        self.assertEqual(self.detector._check_syntax(content), '2.7')

    def test_python3_syntax_not_detected(self):
        content = 'print("hello")\nfor i in range(5): pass'
        self.assertIsNone(self.detector._check_syntax(content))


class TestNormalizeVersion(unittest.TestCase):
    """Тесты normalize_version()."""

    def setUp(self):
        self.detector = PythonVersionDetector()

    def test_27(self):
        self.assertEqual(self.detector.normalize_version('2.7'), '2.7')

    def test_311(self):
        self.assertEqual(self.detector.normalize_version('3.11'), '3.11')

    def test_311_5(self):
        self.assertEqual(self.detector.normalize_version('3.11.5'), '3.11')

    def test_3_only(self):
        self.assertEqual(self.detector.normalize_version('3'), '3.11')


class TestDetectEncoding(unittest.TestCase):
    """Тесты _detect_encoding()."""

    def setUp(self):
        self.detector = PythonVersionDetector()

    def test_utf8_default(self):
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as f:
            f.write(b'print("hello")')
            path = f.name
        try:
            self.assertEqual(self.detector._detect_encoding(path), 'utf-8')
        finally:
            Path(path).unlink(missing_ok=True)

    def test_cp1251_from_comment(self):
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as f:
            f.write('# -*- coding: cp1251 -*-\nprint("test")'.encode('utf-8'))
            path = f.name
        try:
            self.assertEqual(self.detector._detect_encoding(path), 'cp1251')
        finally:
            Path(path).unlink(missing_ok=True)


class TestDetectVersion(unittest.TestCase):
    """Тесты detect_version()."""

    def setUp(self):
        self.detector = PythonVersionDetector()

    def test_shebang_detection(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write('#!/usr/bin/env python2.7\nprint "hello"')
            path = f.name
        try:
            version, method = self.detector.detect_version(path)
            self.assertEqual(version, '2.7')
            self.assertEqual(method, 'shebang')
        finally:
            Path(path).unlink(missing_ok=True)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.detector.detect_version('/nonexistent/path/script.py')


if __name__ == '__main__':
    unittest.main()
