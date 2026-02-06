#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Юнит-тесты для модуля config_loader.
Запуск: python -m unittest tests.test_config_loader
"""

import unittest
import json
import tempfile
from pathlib import Path

from pythondocker.config_loader import (
    find_config,
    load_config,
    apply_config,
    CONFIG_NAMES,
)


class TestFindConfig(unittest.TestCase):
    """Тесты find_config()."""

    def test_find_config_in_same_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / '.pythondocker.json'
            config_path.write_text('{"python": "3.11"}', encoding='utf-8')
            found = find_config(tmp)
            self.assertIsNotNone(found)
            self.assertEqual(found.name, '.pythondocker.json')

    def test_find_config_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = find_config(tmp)
            self.assertIsNone(found)


class TestLoadConfig(unittest.TestCase):
    """Тесты load_config()."""

    def test_load_json_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / '.pythondocker.json'
            config_path.write_text('{"python": "3.11", "encoding": "utf-8"}', encoding='utf-8')
            script_path = tmp + '/subdir/script.py'
            Path(tmp, 'subdir').mkdir(exist_ok=True)
            Path(script_path).touch()
            config, base = load_config(script_path)
            self.assertIsNotNone(config)
            self.assertEqual(config.get('python'), '3.11')
            self.assertEqual(config.get('encoding'), 'utf-8')
            self.assertEqual(str(base), tmp)

    def test_load_config_no_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            script_path = tmp + '/script.py'
            Path(script_path).touch()
            config, base = load_config(script_path)
            self.assertIsNone(config)
            self.assertIsNone(base)


class TestApplyConfig(unittest.TestCase):
    """Тесты apply_config()."""

    def test_apply_python(self):
        config = {'python': '3.11'}
        result = apply_config(config, Path('/tmp'))
        self.assertEqual(result['python_version'], '3.11')

    def test_apply_default_interpreter(self):
        config = {'default_interpreter': 'pypy3.11'}
        result = apply_config(config, Path('/tmp'))
        self.assertEqual(result['python_version'], 'pypy3.11')

    def test_apply_encoding(self):
        config = {'encoding': 'cp1251'}
        result = apply_config(config, Path('/tmp'))
        self.assertEqual(result['encoding'], 'cp1251')

    def test_apply_env_dict(self):
        config = {'env': {'KEY1': 'val1', 'KEY2': 'val2'}}
        result = apply_config(config, Path('/tmp'))
        self.assertEqual(result['env'], {'KEY1': 'val1', 'KEY2': 'val2'})

    def test_apply_docker_true(self):
        config = {'docker': True}
        result = apply_config(config, Path('/tmp'))
        self.assertTrue(result['docker'])

    def test_apply_docker_string_yes(self):
        config = {'docker': 'yes'}
        result = apply_config(config, Path('/tmp'))
        self.assertTrue(result['docker'])

    def test_apply_docker_false(self):
        config = {'docker': False}
        result = apply_config(config, Path('/tmp'))
        self.assertFalse(result['docker'])


if __name__ == '__main__':
    unittest.main()
