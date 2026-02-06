"""Поддержка запуска Jupyter Notebook (.ipynb) как скрипта."""

import json
import tempfile
from pathlib import Path


def ipynb_to_python(notebook_path: str) -> str:
    """
    Конвертирует Jupyter Notebook в Python скрипт.
    
    Args:
        notebook_path: Путь к .ipynb файлу
        
    Returns:
        Содержимое Python скрипта
    """
    path = Path(notebook_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {notebook_path}")
    if path.suffix.lower() != '.ipynb':
        raise ValueError(f"Ожидается .ipynb файл: {notebook_path}")
    
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        nb = json.load(f)
    
    if 'cells' not in nb:
        raise ValueError("Неверный формат notebook: отсутствует 'cells'")
    
    lines = ['# -*- coding: utf-8 -*-', '# Converted from Jupyter Notebook', '']
    
    for cell in nb['cells']:
        cell_type = cell.get('cell_type', 'code')
        source = cell.get('source', [])
        
        if isinstance(source, list):
            cell_content = ''.join(source)
        else:
            cell_content = str(source)
        
        if not cell_content.strip():
            continue
        
        if cell_type == 'code':
            lines.append(cell_content)
            if not cell_content.endswith('\n'):
                lines.append('\n')
            lines.append('\n')
        elif cell_type == 'markdown':
            # Markdown как комментарии
            for line in cell_content.split('\n'):
                lines.append('# ' + line + '\n')
            lines.append('\n')
    
    return ''.join(lines)


def run_notebook_as_script(notebook_path: str, output_dir: str = None) -> Path:
    """
    Конвертирует notebook в временный .py файл и возвращает путь к нему.
    
    Args:
        notebook_path: Путь к .ipynb файлу
        output_dir: Если указан, записать скрипт в эту директорию (для Docker mount)
    
    Returns:
        Path к временному .py файлу (вызывающий код должен удалить после использования)
    """
    import os
    script_content = ipynb_to_python(notebook_path)
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        temp_path = out / f".pythondocker_nb_{os.getpid()}_{id(script_content) & 0xFFFF}.py"
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        return temp_path
    fd, temp_path = tempfile.mkstemp(suffix='.py', prefix='nb_')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(script_content)
        return Path(temp_path)
    except Exception:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise
