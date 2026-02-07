#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест для проверки поддержки любых версий Python.
"""

print("=" * 60)
print("Тест поддержки любых версий Python")
print("=" * 60)

# Тестируем различные версии
test_versions = [
    '2.3',
    '2.4',
    '2.5',
    '3.14',
    '3.15',
    '3.9',
]

print("\nПроверка формирования URL для различных версий Python:\n")

import sys
sys.path.insert(0, 'pythondocker')

from pythondocker.python_installer import PythonInstaller

installer = PythonInstaller()

for version in test_versions:
    print(f"Версия {version}:")
    
    # Получаем доступные версии
    available = installer._find_available_versions(version)
    print(f"  Доступные варианты: {available[:3]}...")  # Показываем первые 3
    
    # Получаем URL
    url = installer.get_python_url(version)
    if url:
        print(f"  ✓ URL найден: {url}")
    else:
        print(f"  ✗ URL не найден")
    
    print()

print("=" * 60)
print("Тест завершен!")
print("=" * 60)
