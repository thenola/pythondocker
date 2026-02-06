#!/usr/bin/env python3
"""
Скрипт для упрощения публикации на PyPI.
Использование: python publish.py [testpypi|pypi]
"""

import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Выполняет команду и выводит результат."""
    print(f"\n{'='*60}")
    print(f"Выполняется: {' '.join(cmd)}")
    print('='*60)
    result = subprocess.run(cmd, check=check)
    return result.returncode == 0

def clean_build():
    """Очищает старые сборки."""
    print("\nОчистка старых сборок...")
    dirs_to_remove = ['build', 'dist']
    files_to_remove = ['*.egg-info']
    
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Удалено: {dir_name}/")
    
    # Удаляем egg-info директории
    for egg_info in Path('.').glob('*.egg-info'):
        if egg_info.is_dir():
            shutil.rmtree(egg_info)
            print(f"Удалено: {egg_info}/")

def build_package():
    """Собирает пакет."""
    print("\nСборка пакета...")
    if not shutil.which('python'):
        print("Ошибка: python не найден в PATH")
        return False
    
    # Проверяем наличие build
    try:
        import build
    except ImportError:
        print("Ошибка: модуль 'build' не установлен")
        print("Установите: pip install build")
        return False
    
    return run_command([sys.executable, '-m', 'build'])

def check_package():
    """Проверяет собранный пакет."""
    print("\nПроверка пакета...")
    try:
        import twine
    except ImportError:
        print("Ошибка: модуль 'twine' не установлен")
        print("Установите: pip install twine")
        return False
    
    dist_files = list(Path('dist').glob('*'))
    if not dist_files:
        print("Ошибка: файлы в dist/ не найдены")
        return False
    
    return run_command([sys.executable, '-m', 'twine', 'check'] + [str(f) for f in dist_files])

def upload_to_testpypi():
    """Публикует на TestPyPI."""
    print("\nПубликация на TestPyPI...")
    dist_files = list(Path('dist').glob('*'))
    if not dist_files:
        print("Ошибка: файлы в dist/ не найдены. Сначала выполните сборку.")
        return False
    
    return run_command([
        sys.executable, '-m', 'twine', 'upload',
        '--repository', 'testpypi'
    ] + [str(f) for f in dist_files], check=False)

def upload_to_pypi():
    """Публикует на PyPI."""
    print("\nПубликация на PyPI...")
    dist_files = list(Path('dist').glob('*'))
    if not dist_files:
        print("Ошибка: файлы в dist/ не найдены. Сначала выполните сборку.")
        return False
    
    print("\nВНИМАНИЕ: Вы публикуете на официальный PyPI!")
    response = input("Продолжить? (yes/no): ")
    if response.lower() != 'yes':
        print("Отменено.")
        return False
    
    return run_command([
        sys.executable, '-m', 'twine', 'upload'
    ] + [str(f) for f in dist_files], check=False)

def main():
    """Главная функция."""
    if len(sys.argv) < 2:
        print("Использование: python publish.py [clean|build|check|testpypi|pypi|all]")
        print("\nКоманды:")
        print("  clean     - Очистить старые сборки")
        print("  build     - Собрать пакет")
        print("  check     - Проверить собранный пакет")
        print("  testpypi  - Опубликовать на TestPyPI")
        print("  pypi      - Опубликовать на PyPI")
        print("  all       - Выполнить все шаги (clean, build, check)")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'clean':
        clean_build()
    elif command == 'build':
        clean_build()
        if not build_package():
            sys.exit(1)
    elif command == 'check':
        if not check_package():
            sys.exit(1)
    elif command == 'testpypi':
        if not upload_to_testpypi():
            sys.exit(1)
    elif command == 'pypi':
        if not upload_to_pypi():
            sys.exit(1)
    elif command == 'all':
        clean_build()
        if not build_package():
            sys.exit(1)
        if not check_package():
            sys.exit(1)
        print("\n✓ Сборка завершена успешно!")
        print("\nДля публикации используйте:")
        print("  python publish.py testpypi  # Для тестирования")
        print("  python publish.py pypi      # Для публикации")
    else:
        print(f"Неизвестная команда: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
