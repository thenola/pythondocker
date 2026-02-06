#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска всех тестов PythonDocker
"""

import os
import sys
import subprocess
from pathlib import Path

# Добавляем корень проекта в sys.path (для запуска из tests/ или из корня)
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


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

# Модули юнит-тестов (исключены интеграционные скрипты на Python 2)
UNIT_TEST_MODULES = [
    'tests.test_version_detector',
    'tests.test_config_loader',
    'tests.test_notebook_runner',
    'tests.test_docker_runner',
    'tests.test_commands',
    'tests.test_pyenv_manager',
    'tests.test_alternative_interpreters',
    'tests.test_cli',
]


def run_unit_tests():
    """Запускает юнит-тесты через unittest (только модули, не discover)."""
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for module_name in UNIT_TEST_MODULES:
        try:
            suite.addTests(loader.loadTestsFromName(module_name))
        except Exception as e:
            print(f"Ошибка загрузки {module_name}: {e}")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def main():
    """Запускает все тесты."""
    tests_dir = Path(__file__).parent

    # 1. Юнит-тесты (unittest)
    print("\n" + "=" * 60)
    print("ЮНИТ-ТЕСТЫ (unittest)")
    print("=" * 60)
    unit_ok = run_unit_tests()

    # 2. Интеграционные тесты (запуск скриптов через pythondocker)
    test_files = sorted(tests_dir.glob('test_*.py'))
    integration_tests = [
        f for f in test_files
        if f.name not in (
            'run_all_tests.py',
            'test_alternative_interpreters.py',
            'test_version_detector.py',
            'test_config_loader.py',
            'test_notebook_runner.py',
            'test_docker_runner.py',
            'test_commands.py',
            'test_pyenv_manager.py',
            'test_cli.py',
        )
    ]

    print(f"\n{'='*60}")
    print(f"ИНТЕГРАЦИОННЫЕ ТЕСТЫ ({len(integration_tests)} шт.)")
    print('='*60)

    results = []
    for test_file in integration_tests:
        success = run_test(test_file)
        results.append((test_file.name, success))
    
    # Выводим итоги
    print(f"\n{'='*60}")
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print('='*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "[OK] PASS" if success else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print(f"\nИнтеграционные: пройдено {passed}/{total}")
    print(f"Юнит-тесты: {'OK' if unit_ok else 'FAIL'}")

    all_ok = unit_ok and (passed == total)
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
