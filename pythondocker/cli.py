"""CLI интерфейс для PythonDocker."""

import argparse
import sys
import os
from pathlib import Path
from .version_detector import PythonVersionDetector
from .environment_manager import EnvironmentManager
from .commands import Commands


def main():
    """Главная функция CLI."""
    # Проверяем, является ли первый аргумент командой
    commands = ['list', 'info', 'clean', 'remove']
    if len(sys.argv) > 1 and sys.argv[1] in commands:
        # Обрабатываем команды
        command = sys.argv[1]
        
        if command == 'list':
            commands_obj = Commands()
            envs = commands_obj.list_environments()
            if envs:
                print(f"\nНайдено окружений: {len(envs)}\n")
                print(f"{'Имя':<30} {'Версия':<20} {'Размер':<15}")
                print("-" * 65)
                for env in envs:
                    size_str = commands_obj.format_size(env['size'])
                    print(f"{env['name']:<30} {env['version']:<20} {size_str:<15}")
            else:
                print("Окружения не найдены")
            return
        
        if command == 'info':
            commands_obj = Commands()
            info = commands_obj.info()
            print("\n=== Информация о PythonDocker ===\n")
            print(f"Установлено версий Python: {info['python_versions']}")
            print(f"Создано окружений: {info['environments']}")
            print(f"Директория Python: {info['python_dir']}")
            print(f"Директория окружений: {info['envs_dir']}")
            print(f"Pyenv доступен: {'Да' if info['pyenv_available'] else 'Нет'}")
            
            versions = commands_obj.list_python_versions()
            if versions:
                print(f"\nУстановленные версии Python:")
                for v in versions:
                    size_str = commands_obj.format_size(v['size'])
                    print(f"  - {v['version']:<10} ({size_str})")
            return
        
        if command == 'clean':
            dry_run = '--dry-run' in sys.argv
            commands_obj = Commands()
            removed = commands_obj.clean_environments(dry_run=dry_run)
            if dry_run:
                print(f"\nБудет удалено окружений: {removed}")
            else:
                print(f"\nУдалено окружений: {removed}")
            return
        
        if command == 'remove':
            if len(sys.argv) < 3:
                print("Ошибка: укажите версию Python для удаления")
                print("Использование: pythondocker remove <version> [--dry-run]")
                sys.exit(1)
            version = sys.argv[2]
            dry_run = '--dry-run' in sys.argv
            commands_obj = Commands()
            commands_obj.remove_python_version(version, dry_run=dry_run)
            return
    
    # Обычный режим запуска скрипта
    parser = argparse.ArgumentParser(
        description='Запуск Python скриптов в изолированных виртуальных окружениях',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  pythondocker script.py                    # Автоматическое определение версии
  pythondocker script.py --python 2.7       # Указать версию вручную
  pythondocker script.py --requirements req.txt  # С зависимостями
  pythondocker script.py --force-recreate   # Пересоздать окружение
  pythondocker script.py --encoding cp1251  # Указать кодировку (Windows)
  pythondocker script.py -e utf-8           # Указать кодировку (краткая форма)
  
Дополнительные команды:
  pythondocker list                          # Список всех окружений
  pythondocker info                          # Информация о системе
  pythondocker clean                         # Очистка старых окружений
  pythondocker remove <version>              # Удалить версию Python
        """
    )
    
    parser.add_argument(
        'script',
        help='Путь к Python скрипту для запуска'
    )
    
    parser.add_argument(
        '--python', '-p',
        dest='python_version',
        help='Версия Python (например, 2.7, 3.11). Если не указана, определяется автоматически'
    )
    
    parser.add_argument(
        '--requirements', '-r',
        dest='requirements',
        help='Путь к файлу requirements.txt с зависимостями'
    )
    
    parser.add_argument(
        '--args',
        nargs=argparse.REMAINDER,
        help='Аргументы для передаваемые скрипту'
    )
    
    parser.add_argument(
        '--env',
        nargs='*',
        metavar='KEY=VALUE',
        help='Переменные окружения в формате KEY=VALUE'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод'
    )
    
    parser.add_argument(
        '--force-recreate',
        action='store_true',
        help='Пересоздать окружение если оно уже существует'
    )
    
    parser.add_argument(
        '--encoding', '-e',
        dest='encoding',
        default=None,
        help='Кодировка для запуска скрипта (например, utf-8, cp1251, latin1). По умолчанию используется системная кодировка'
    )
    
    args = parser.parse_args()
    
    # Проверяем существование скрипта
    if not os.path.exists(args.script):
        print(f"Ошибка: Скрипт не найден: {args.script}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Определяем версию Python и кодировку
        detector = PythonVersionDetector()
        
        if args.python_version:
            python_version = args.python_version
            detection_method = 'manual'
        else:
            python_version, detection_method = detector.detect_version(args.script)
            python_version = detector.normalize_version(python_version)
            if args.verbose:
                print(f"Определена версия Python: {python_version} (метод: {detection_method})")
        
        # Определяем кодировку из файла если не указана вручную
        if not args.encoding:
            detected_encoding = detector._detect_encoding(args.script)
            if detected_encoding != 'utf-8' or args.verbose:
                print(f"Определена кодировка файла: {detected_encoding}")
            args.encoding = detected_encoding
        
        # Парсим переменные окружения
        env_vars = {}
        if args.env:
            for env_pair in args.env:
                if '=' in env_pair:
                    key, value = env_pair.split('=', 1)
                    env_vars[key] = value
        
        # Запускаем скрипт в изолированном окружении
        env_manager = EnvironmentManager()
        
        # Создаем окружение с возможностью пересоздания
        env_dir = env_manager.create_environment(
            python_version=python_version,
            force_recreate=args.force_recreate
        )
        
        exit_code = env_manager.run_script(
            script_path=args.script,
            python_version=python_version,
            args=args.args,
            env_vars=env_vars if env_vars else None,
            requirements_path=args.requirements,
            encoding=args.encoding
        )
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nПрервано пользователем", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
