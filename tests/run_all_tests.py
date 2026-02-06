#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска всех тестов PythonDocker
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test(test_file):
    """Запускает один тест и возвращает результат."""
    print(f"\n{'='*60}")
    print(f"Запуск теста: {test_file}")
    print('='*60)
    
    # Определяем параметры для разных тестов
    test_name = Path(test_file).stem
    
    cmd = ['pythondocker', str(test_file)]
    
    if 'python2' in test_name or 'encoding' in test_name or 'syntax' in test_name:
        cmd.extend(['--python', '2.7'])
    
    if 'encoding' in test_name:
        cmd.extend(['--encoding', 'cp1251'])
    
    if 'requirements' in test_name:
        # Используем абсолютный путь к requirements.txt
        tests_dir = Path(__file__).parent
        req_path = tests_dir / 'requirements_test.txt'
        cmd.extend(['--requirements', str(req_path)])
    
    if 'args' in test_name:
        cmd.extend(['--args', 'test_arg1', 'test_arg2', 'test_arg3'])
    
    if 'env' in test_name:
        cmd.extend(['--env', 'TEST_VAR=test_value', 'DEBUG=true'])
    
    print(f"Команда: {' '.join(cmd)}")
    
    try:
        # Для интерактивных тестов не используем DEVNULL
        stdin_param = None
        if 'input' in test_name.lower():
            stdin_param = None  # Используем реальный stdin для интерактивных
        else:
            stdin_param = subprocess.DEVNULL  # Закрываем stdin для неинтерактивных
        
        result = subprocess.run(
            cmd,
            capture_output=False,  # Показываем вывод в реальном времени
            text=True,
            timeout=60,
            stdin=stdin_param
        )
        
        # Проверяем код возврата
        success = result.returncode == 0
        
        # Для теста кодировки выводим дополнительную информацию
        if 'encoding' in test_name and not success:
            print(f"\nВНИМАНИЕ: Тест кодировки завершился с кодом {result.returncode}")
            print("Это может быть связано с особенностями обработки кодировки в тестовом окружении")
            print("Попробуйте запустить тест напрямую: pythondocker tests/test_encoding_cp1251.py --python 2.7 --encoding cp1251")
        
        return success
    except subprocess.TimeoutExpired:
        print(f"ТЕСТ ПРЕРВАН: превышено время ожидания")
        return False
    except Exception as e:
        print(f"ОШИБКА при запуске теста: {e}")
        return False

def main():
    """Запускает все тесты."""
    tests_dir = Path(__file__).parent
    test_files = sorted(tests_dir.glob('test_*.py'))
    
    if not test_files:
        print("Тестовые файлы не найдены!")
        return 1
    
    print(f"\nНайдено тестов: {len(test_files)}")
    print("Запуск тестов...\n")
    
    results = []
    for test_file in test_files:
        # Пропускаем сам run_all_tests.py
        if test_file.name == 'run_all_tests.py':
            continue
        
        success = run_test(test_file)
        results.append((test_file.name, success))
    
    # Выводим итоги
    print(f"\n{'='*60}")
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print('='*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ ПРОЙДЕН" if success else "✗ ПРОВАЛЕН"
        print(f"{status}: {test_name}")
    
    print(f"\nПройдено: {passed}/{total}")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
