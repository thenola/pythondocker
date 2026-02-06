#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Юнит-тесты для модуля notebook_runner.
Запуск: python -m unittest tests.test_notebook_runner
"""

import unittest
import json
import tempfile
from pathlib import Path

from pythondocker.notebook_runner import ipynb_to_python, run_notebook_as_script


def make_notebook(code_cells=None, markdown_cells=None):
    """Создаёт минимальный JSON ноутбука."""
    cells = []
    if code_cells:
        for code in code_cells:
            cells.append({'cell_type': 'code', 'source': code if isinstance(code, list) else [code]})
    if markdown_cells:
        for md in markdown_cells:
            cells.append({'cell_type': 'markdown', 'source': md if isinstance(md, list) else [md]})
    return {'cells': cells or [{'cell_type': 'code', 'source': ['print(1)']}]}


class TestIpnbToPython(unittest.TestCase):
    """Тесты ipynb_to_python()."""

    def test_basic_code_cell(self):
        nb = make_notebook(code_cells=['print("hello")\n'])
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False, encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False)
            path = f.name
        try:
            result = ipynb_to_python(path)
            self.assertIn('print("hello")', result)
            self.assertIn('# Converted from Jupyter Notebook', result)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_markdown_as_comment(self):
        nb = make_notebook(code_cells=['x=1'], markdown_cells=['# Title'])
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False, encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False)
            path = f.name
        try:
            result = ipynb_to_python(path)
            self.assertIn('# # Title', result)
            self.assertIn('x=1', result)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            ipynb_to_python('/nonexistent/notebook.ipynb')

    def test_wrong_extension(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print(1)')
            path = f.name
        try:
            with self.assertRaises(ValueError) as ctx:
                ipynb_to_python(path)
            self.assertIn('ipynb', str(ctx.exception))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_no_cells(self):
        nb = {}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False, encoding='utf-8') as f:
            json.dump(nb, f)
            path = f.name
        try:
            with self.assertRaises(ValueError) as ctx:
                ipynb_to_python(path)
            self.assertIn('cells', str(ctx.exception))
        finally:
            Path(path).unlink(missing_ok=True)


class TestRunNotebookAsScript(unittest.TestCase):
    """Тесты run_notebook_as_script()."""

    def test_temp_output(self):
        nb = make_notebook(code_cells=['print(42)'])
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False, encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False)
            path = f.name
        try:
            result = run_notebook_as_script(path)
            self.assertTrue(result.exists())
            self.assertEqual(result.suffix, '.py')
            content = result.read_text(encoding='utf-8')
            self.assertIn('print(42)', content)
            result.unlink(missing_ok=True)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_output_dir(self):
        nb = make_notebook(code_cells=['x=1'])
        with tempfile.TemporaryDirectory() as tmp:
            nb_path = Path(tmp) / 'test.ipynb'
            nb_path.write_text(json.dumps(nb, ensure_ascii=False), encoding='utf-8')
            out_dir = Path(tmp) / 'out'
            result = run_notebook_as_script(str(nb_path), output_dir=str(out_dir))
            self.assertTrue(result.exists())
            self.assertEqual(result.parent, out_dir)
            self.assertIn('x=1', result.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
