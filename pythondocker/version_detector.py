"""Модуль для определения версии Python из скрипта."""

import re
import os
from typing import Optional, Tuple


class PythonVersionDetector:
    """Определяет версию Python из скрипта."""
    
    # Паттерны для определения версии Python
    SHEBANG_PATTERN = re.compile(r'^#!\s*/usr/bin/env\s+python(\d+(?:\.\d+)?)?')
    SHEBANG_PATTERN_ALT = re.compile(r'^#!\s*/usr/bin/python(\d+(?:\.\d+)?)?')
    VERSION_COMMENT_PATTERN = re.compile(r'#.*python\s*(\d+(?:\.\d+)?)', re.IGNORECASE)
    
    # Синтаксические признаки Python 2
    PYTHON2_SYNTAX = [
        r'print\s+[^(]',  # print без скобок
        r'\.iteritems\(\)',  # dict.iteritems()
        r'\.iterkeys\(\)',  # dict.iterkeys()
        r'\.itervalues\(\)',  # dict.itervalues()
        r'xrange\s*\(',  # xrange вместо range
        r'unicode\s*\(',  # unicode() функция
        r'basestring',  # basestring тип
        r'\.has_key\s*\(',  # dict.has_key()
        r'raw_input\s*\(',  # raw_input вместо input
    ]
    
    # Паттерн для определения кодировки из комментария
    CODING_PATTERN = re.compile(r'coding[=:]\s*([-\w.]+)', re.IGNORECASE)
    
    def __init__(self):
        self.python2_patterns = [re.compile(pattern) for pattern in self.PYTHON2_SYNTAX]
    
    def _detect_encoding(self, script_path: str) -> str:
        """
        Определяет кодировку файла из комментария coding.
        
        Args:
            script_path: Путь к скрипту
            
        Returns:
            Кодировка (по умолчанию 'utf-8')
        """
        try:
            # Читаем первые две строки для поиска комментария coding
            with open(script_path, 'rb') as f:
                # Читаем первые 1024 байта
                first_bytes = f.read(1024)
                
            # Пробуем декодировать разными способами для поиска комментария coding
            first_lines = None
            encodings_to_try = ['utf-8', 'cp1251', 'latin1', 'utf-16', 'utf-16-le']
            
            for enc in encodings_to_try:
                try:
                    first_lines = first_bytes.decode(enc, errors='ignore').split('\n')[:2]
                    break
                except:
                    continue
            
            if not first_lines:
                # В крайнем случае используем latin1 (читает любые байты)
                first_lines = first_bytes.decode('latin1', errors='ignore').split('\n')[:2]
            
            # Ищем комментарий coding в первых двух строках
            for line in first_lines:
                match = self.CODING_PATTERN.search(line)
                if match:
                    encoding = match.group(1).lower()
                    # Нормализуем названия кодировок
                    encoding_map = {
                        'utf8': 'utf-8',
                        'utf-8': 'utf-8',
                        'cp1251': 'cp1251',
                        'windows-1251': 'cp1251',
                        'latin1': 'latin1',
                        'iso-8859-1': 'latin1',
                    }
                    return encoding_map.get(encoding, encoding)
        except Exception:
            pass
        
        # По умолчанию UTF-8
        return 'utf-8'
    
    def detect_version(self, script_path: str) -> Tuple[str, str]:
        """
        Определяет версию Python из скрипта.
        
        Args:
            script_path: Путь к Python скрипту
            
        Returns:
            Tuple[str, str]: (версия, метод определения)
            Например: ('2.7', 'shebang') или ('3.11', 'syntax')
        """
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Скрипт не найден: {script_path}")
        
        # Пытаемся определить кодировку из файла
        detected_encoding = self._detect_encoding(script_path)
        
        # Читаем файл с правильной кодировкой
        # Важно: используем errors='replace' чтобы не падать на неправильных символах
        lines = None
        encodings_to_try = [detected_encoding, 'utf-8', 'cp1251', 'latin1']
        
        for enc in encodings_to_try:
            try:
                with open(script_path, 'r', encoding=enc, errors='replace') as f:
                    lines = f.readlines()
                    break
            except (UnicodeDecodeError, LookupError, ValueError):
                continue
        
        if lines is None:
            # В крайнем случае используем latin1 (читает любые байты)
            with open(script_path, 'r', encoding='latin1', errors='replace') as f:
                lines = f.readlines()
        
        # Метод 1: Проверка shebang
        if lines:
            version = self._check_shebang(lines[0])
            if version:
                return version, 'shebang'
        
        # Метод 2: Поиск комментариев с версией
        for line in lines[:20]:  # Проверяем первые 20 строк
            version = self._check_version_comment(line)
            if version:
                return version, 'comment'
        
        # Метод 3: Анализ синтаксиса
        script_content = ''.join(lines)
        version = self._check_syntax(script_content)
        if version:
            return version, 'syntax'
        
        # По умолчанию используем Python 3
        return '3.11', 'default'
    
    def _check_shebang(self, first_line: str) -> Optional[str]:
        """Проверяет shebang строку."""
        match = self.SHEBANG_PATTERN.match(first_line) or self.SHEBANG_PATTERN_ALT.match(first_line)
        if match:
            version = match.group(1)
            if version:
                # Нормализуем версию
                if version.startswith('2'):
                    return '2.7'
                elif version.startswith('3'):
                    return '3.11' if not version[1:] else version
            else:
                # Если версия не указана, предполагаем Python 3
                return '3.11'
        return None
    
    def _check_version_comment(self, line: str) -> Optional[str]:
        """Проверяет комментарии на наличие версии."""
        match = self.VERSION_COMMENT_PATTERN.search(line)
        if match:
            version = match.group(1)
            if version.startswith('2'):
                return '2.7'
            elif version.startswith('3'):
                return '3.11' if len(version) == 1 else version
        return None
    
    def _check_syntax(self, content: str) -> Optional[str]:
        """Анализирует синтаксис для определения версии Python."""
        python2_matches = sum(1 for pattern in self.python2_patterns if pattern.search(content))
        
        # Если найдено много признаков Python 2, вероятно это Python 2
        if python2_matches >= 2:
            return '2.7'
        
        return None
    
    def normalize_version(self, version: str) -> str:
        """
        Нормализует версию Python для использования в Docker образах.
        
        Args:
            version: Версия Python (например, '2.7', '3.11', 'pypy3.11', 'jython')
            
        Returns:
            Нормализованная версия для Docker образа
        """
        v = version.lower().strip()
        # Альтернативные интерпретаторы
        if v.startswith('pypy'):
            vc = v.replace(' ', '')
            for key in ('pypy3.11', 'pypy3.10', 'pypy3.9', 'pypy2.7'):
                if key == vc or (vc in key and key.startswith(vc)) or key.startswith(vc):
                    return key
            if '3.11' in v or '311' in v:
                return 'pypy3.11'
            if '3.10' in v or '310' in v:
                return 'pypy3.10'
            if '3.9' in v or '39' in v:
                return 'pypy3.9'
            if '2' in v or '27' in v:
                return 'pypy2.7'
            return 'pypy3.11'
        if v.startswith('jython'):
            return 'jython2.7'
        # CPython
        if v.startswith('2'):
            return '2.7'
        elif v.startswith('3'):
            parts = version.split('.')
            if len(parts) >= 2:
                return f"{parts[0]}.{parts[1]}"
            return '3.11'
        return '3.11'
