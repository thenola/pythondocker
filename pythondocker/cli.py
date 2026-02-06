"""CLI интерфейс для PythonDocker."""

import argparse
import sys
import os
import atexit
from pathlib import Path
from . import __version__
from .version_detector import PythonVersionDetector
from .environment_manager import EnvironmentManager
from .commands import Commands
from .notebook_runner import run_notebook_as_script
from .config_loader import load_config, apply_config
from . import docker_runner

def main():
    """Главная функция CLI."""
    # Обработка -v / --version
    if '-v' in sys.argv or '--version' in sys.argv:
        print(f"PythonDocker {__version__}")
        print(f"https://github.com/thenola/pythondocker")
        return

    # Проверяем, является ли первый аргумент командой
    commands = ['list', 'info', 'clean', 'remove', 'freeze', 'completions', 'help']
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
            print(f"Docker доступен: {'Да' if docker_runner.docker_available() else 'Нет'}")
            
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
        
        if command == 'freeze':
            freeze_parser = argparse.ArgumentParser(
                prog='pythondocker freeze',
                description='Экспорт установленных пакетов (pip freeze) в requirements.txt.',
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog='Примеры:  pythondocker freeze -p 3.11 -o req.txt   pythondocker freeze -c'
            )
            freeze_parser.add_argument('--python', '-p', default=None, metavar='VER',
                help='Версия Python для окружения (например, 2.7, 3.11)')
            freeze_parser.add_argument('--output', '-o', default=None, metavar='FILE',
                help='Файл для вывода списка пакетов (по умолчанию — stdout)')
            freeze_parser.add_argument('--current', '-c', action='store_true',
                help='Использовать текущий интерпретатор (окружение, в котором запущен pythondocker)')
            freeze_parser.add_argument('script', nargs='?', default=None, metavar='SCRIPT',
                help='Скрипт для автоопределения версии Python')
            freeze_args = freeze_parser.parse_args(sys.argv[2:])
            
            if freeze_args.current:
                python_version = None
            else:
                detector = PythonVersionDetector()
                if freeze_args.python:
                    python_version = detector.normalize_version(freeze_args.python)
                elif freeze_args.script and os.path.exists(freeze_args.script):
                    python_version, _ = detector.detect_version(freeze_args.script)
                    python_version = detector.normalize_version(python_version)
                    print(f"Версия Python определена из скрипта: {python_version}")
                else:
                    python_version = '3.11'
                    print(f"Используется версия по умолчанию: {python_version}")
            
            commands_obj = Commands()
            success = commands_obj.freeze(python_version, freeze_args.output, freeze_args.current)
            sys.exit(0 if success else 1)
        
        if command == 'help':
            pkg_dir = Path(__file__).resolve().parent
            for manual_path in [pkg_dir / 'MANUAL.md', pkg_dir.parent / 'MANUAL.md']:
                if manual_path.exists():
                    print(manual_path.read_text(encoding='utf-8'))
                    return
            print("Справка: pythondocker --help")
            print("Репозиторий: https://github.com/thenola/pythondocker")
            return

        if command == 'completions':
            shell = sys.argv[2] if len(sys.argv) > 2 else 'bash'
            script_map = {'bash': 'pythondocker.bash', 'zsh': 'pythondocker.zsh', 'powershell': 'pythondocker.ps1', 'ps1': 'pythondocker.ps1'}
            script_name = script_map.get(shell.lower(), 'pythondocker.bash')
            script_path = Path(__file__).parent.parent / 'completions' / script_name
            if not script_path.exists():
                script_path = Path(__file__).parent / 'completions' / script_name
            if script_path.exists():
                print(script_path.read_text(encoding='utf-8'))
            else:
                print(f"Shell {shell} не поддерживается. Используйте: bash, zsh, powershell", file=sys.stderr)
                sys.exit(1)
            return
    
    # Обычный режим запуска скрипта
    parser = argparse.ArgumentParser(
        prog='pythondocker',
        description='PythonDocker — запуск .py и .ipynb в изолированных venv или Docker.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument_group('synopsis', description="""  pythondocker [OPTIONS] [SCRIPT] [--args ARG1 ARG2 ...]
  pythondocker <COMMAND> [OPTIONS]""")

    parser.add_argument_group('commands', description="""  list                  Список окружений (имя, версия, размер)
  info                  Установленные Python, директории, pyenv, Docker
  clean [--dry-run]     Удалить окружения старше 30 дней
  remove <version>      Удалить версию Python (2.7, 3.11, pypy3.11, jython)
  freeze [-p VER] [-o FILE] [-c]   Экспорт зависимостей (pip freeze)
  completions SHELL     Автодополнение: bash, zsh, powershell
  help                  Подробная справка (MANUAL.md)""")

    parser.add_argument_group('options summary', description="""  -p, --python VER      Версия: 2.7, 3.8–3.13, pypy3.11, jython
  -r, --requirements    requirements.txt
  -e, --encoding        Кодировка (utf-8, cp1251, cp866)
  --args ...            Аргументы скрипту (после --args)
  --env KEY=VALUE       Переменные окружения
  --docker              Запуск в Docker вместо venv
  --shell               Интерактивный Python shell
  -l, --log-file FILE   Лог stdout/stderr в файл
  --offline             Только установленные версии
  --force-recreate      Пересоздать окружение
  -v, --version         Версия и URL: github.com/thenola/pythondocker""")

    parser.add_argument_group('interpreter versions', description="""  CPython: 2.7, 3.6–3.13 | PyPy: pypy2.7, pypy3.9–3.11 | Jython: jython""")

    parser.add_argument_group('configuration', description="""  .pythondocker.yml / .pythondocker.json — python, requirements, encoding, env, docker""")

    parser.add_argument_group('examples', description="""  pythondocker script.py
  pythondocker script.py -p 2.7 -r requirements.txt
  pythondocker script.py --encoding cp1251 -l out.log
  pythondocker --shell -p 3.11
  pythondocker script.py --docker
  pythondocker freeze -c -o requirements.txt
  pythondocker help""")

    pos = parser.add_argument_group('аргументы')
    pos.add_argument(
        'script',
        nargs='?',
        default=None,
        metavar='SCRIPT',
        help='Путь к .py или .ipynb; при отсутствии требуется --shell'
    )

    run = parser.add_argument_group('запуск и интерпретатор')
    run.add_argument(
        '--shell',
        action='store_true',
        help='Запустить интерактивную оболочку Python в окружении'
    )
    run.add_argument(
        '--python', '-p',
        dest='python_version',
        metavar='VER',
        help='Версия интерпретатора (2.7, 3.11, pypy3.11, jython); иначе — автоопределение'
    )
    run.add_argument(
        '--args',
        nargs=argparse.REMAINDER,
        help='Аргументы, передаваемые скрипту после --args'
    )

    deps = parser.add_argument_group('зависимости и окружение')
    deps.add_argument(
        '--requirements', '-r',
        dest='requirements',
        metavar='FILE',
        help='Путь к requirements.txt для установки зависимостей'
    )
    deps.add_argument(
        '--no-deps',
        action='store_true',
        help='Не устанавливать зависимости из requirements.txt'
    )
    deps.add_argument(
        '--env',
        nargs='*',
        metavar='KEY=VALUE',
        help='Переменные окружения для процесса (можно несколько)'
    )

    opts = parser.add_argument_group('опции выполнения')
    opts.add_argument(
        '--encoding', '-e',
        dest='encoding',
        metavar='CODEC',
        default=None,
        help='Кодировка ввода/вывода скрипта (utf-8, cp1251, latin1 и т.д.)'
    )
    opts.add_argument(
        '--force-recreate',
        action='store_true',
        help='Пересоздать окружение, если оно уже существует'
    )
    opts.add_argument(
        '--offline',
        action='store_true',
        help='Не загружать новые версии Python; использовать только установленные'
    )
    opts.add_argument(
        '--docker',
        action='store_true',
        dest='docker',
        help='Запустить скрипт в Docker-контейнере (python:X-slim) вместо venv'
    )

    out = parser.add_argument_group('вывод и отладка')
    out.add_argument(
        '--version', '-v',
        action='store_true',
        dest='show_version',
        help='Показать версию и URL репозитория'
    )
    out.add_argument(
        '--verbose',
        action='store_true',
        help='Расширенный вывод'
    )
    out.add_argument(
        '--debug', '-d',
        action='store_true',
        dest='debug',
        help='Служебные сообщения: создание окружения, версия Python, кодировка'
    )
    out.add_argument(
        '--log-file', '-l',
        dest='log_file',
        metavar='FILE',
        default=None,
        help='Дублировать stdout и stderr в указанный файл'
    )
    
    args = parser.parse_args()

    if getattr(args, 'show_version', False):
        print(f"PythonDocker {__version__}")
        print(f"https://github.com/thenola/pythondocker")
        return

    # Режим --shell: интерактивная оболочка
    if args.shell:
        try:
            detector = PythonVersionDetector()
            python_version = detector.normalize_version(args.python_version or '3.11')
            if args.python_version:
                print(f"Используется Python: {python_version}")
            if use_docker:
                sys.exit(docker_runner.run_shell_in_docker(
                    python_version, cwd=None, quiet=not args.debug))
            else:
                env_manager = EnvironmentManager()
                sys.exit(env_manager.run_shell(python_version, quiet=not args.debug, offline=getattr(args, 'offline', False)))
        except KeyboardInterrupt:
            sys.exit(130)
        except Exception as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Проверяем наличие скрипта
    if not args.script:
        print("Ошибка: укажите скрипт для запуска или используйте --shell", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(args.script):
        print(f"Ошибка: Файл не найден: {args.script}", file=sys.stderr)
        sys.exit(1)
    
    applied = {}
    # Загружаем конфигурацию из .pythondocker.yml / .pythondocker.json
    config, config_base = load_config(args.script)
    if config and config_base:
        applied = apply_config(config, config_base)
        if args.verbose and not args.debug:
            print(f"Загружена конфигурация из {config_base}")
        if not args.python_version:
            args.python_version = applied.get('python_version') or applied.get('default_interpreter')
        if not args.requirements and applied.get('requirements'):
            args.requirements = applied['requirements']
        if not args.encoding and applied.get('encoding'):
            args.encoding = applied['encoding']
        if not args.env and applied.get('env'):
            args.env = [f"{k}={v}" for k, v in applied['env'].items()]
        elif args.env and applied.get('env'):
            env_dict = dict(applied['env'])
            for pair in args.env:
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    env_dict[k] = v
            args.env = [f"{k}={v}" for k, v in env_dict.items()]
        if not getattr(args, 'docker', False) and applied.get('docker'):
            args.docker = True

    use_docker = getattr(args, 'docker', False)

    try:
        script_path = args.script
        temp_script_path = None
        
        # Jupyter Notebook: конвертируем в .py
        if Path(script_path).suffix.lower() == '.ipynb':
            if args.verbose or args.debug:
                print("Конвертация Jupyter Notebook в Python скрипт...")
            # Для Docker: скрипт должен быть в директории ноутбука (монтируется в контейнер)
            output_dir = str(Path(script_path).parent) if use_docker else None
            temp_script_path = run_notebook_as_script(script_path, output_dir=output_dir)
            script_path = str(temp_script_path)
            atexit.register(lambda: temp_script_path.unlink(missing_ok=True))
        
        # Определяем версию Python и кодировку
        detector = PythonVersionDetector()
        
        if args.python_version:
            python_version = args.python_version
            detection_method = 'manual'
        else:
            # Для .ipynb по умолчанию Python 3
            if Path(args.script).suffix.lower() == '.ipynb':
                python_version = '3.11'
                detection_method = 'notebook'
            else:
                python_version, detection_method = detector.detect_version(script_path)
            python_version = detector.normalize_version(python_version)
            if args.verbose or args.debug:
                print(f"Определена версия Python: {python_version} (метод: {detection_method})")
        
        # Определяем кодировку из файла если не указана вручную
        if not args.encoding:
            detected_encoding = detector._detect_encoding(script_path)
            if detected_encoding != 'utf-8' or args.verbose or args.debug:
                print(f"Определена кодировка файла: {detected_encoding}")
            args.encoding = detected_encoding
        
        # Парсим переменные окружения
        env_vars = {}
        if args.env:
            for env_pair in args.env:
                if '=' in env_pair:
                    key, value = env_pair.split('=', 1)
                    env_vars[key] = value
        
        work_dir = str(Path(args.script).parent) if Path(args.script).suffix.lower() == '.ipynb' else None
        display_name = Path(args.script).name if Path(args.script).suffix.lower() == '.ipynb' else None

        if use_docker:
            exit_code = docker_runner.run_in_docker(
                script_path=script_path,
                python_version=python_version,
                args=args.args,
                env_vars=env_vars if env_vars else None,
                requirements_path=args.requirements,
                encoding=args.encoding,
                work_dir=work_dir,
                script_display_name=display_name,
                log_file=args.log_file,
                quiet=not args.debug,
                no_deps=args.no_deps,
            )
        else:
            env_manager = EnvironmentManager()
            env_manager.create_environment(
                python_version=python_version,
                force_recreate=args.force_recreate,
                quiet=not args.debug,
                offline=getattr(args, 'offline', False)
            )
            exit_code = env_manager.run_script(
                script_path=script_path,
                python_version=python_version,
                args=args.args,
                env_vars=env_vars if env_vars else None,
                requirements_path=args.requirements,
                encoding=args.encoding,
                no_deps=args.no_deps,
                work_dir=work_dir,
                script_display_name=display_name,
                log_file=args.log_file,
                quiet=not args.debug,
                offline=getattr(args, 'offline', False),
                config_interpreter_opts=applied
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
