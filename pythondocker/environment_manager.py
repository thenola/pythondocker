"""Модуль для создания и управления изолированными окружениями Python."""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict
from .python_installer import PythonInstaller
from . import alternative_interpreters


class EnvironmentManager:
    """Управляет изолированными окружениями для запуска Python скриптов."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Инициализирует менеджер окружений.
        
        Args:
            base_dir: Базовая директория для окружений (по умолчанию ~/.pythondocker/envs)
        """
        if base_dir is None:
            home_dir = Path.home()
            base_dir = home_dir / '.pythondocker' / 'envs'
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.python_installer = PythonInstaller()
    
    def create_environment(self, python_version: str, env_name: Optional[str] = None, force_recreate: bool = False, quiet: bool = False, offline: bool = False) -> Path:
        """
        Создает изолированное виртуальное окружение.
        
        Args:
            python_version: Версия Python (например, '2.7', '3.11', 'pypy3.11', 'jython')
            env_name: Имя окружения (по умолчанию генерируется автоматически)
            force_recreate: Пересоздать окружение если оно уже существует
            
        Returns:
            Path к директории окружения
        """
        # Jython не использует venv — устанавливаем jar и возвращаем фиктивную директорию
        if alternative_interpreters.is_alternative_interpreter(python_version) == 'jython':
            self.python_installer.install_python(python_version, use_pyenv=False, quiet=quiet, offline=offline)
            return self.base_dir / "python-jython"
        
        if env_name is None:
            env_name = f"python-{python_version.replace('.', '-')}"
        
        env_dir = self.base_dir / env_name
        
        # Проверяем существующее окружение
        if env_dir.exists() and not force_recreate:
            # Проверяем версию Python в существующем окружении
            python_exe = self.get_python_executable(env_dir)
            if python_exe.exists():
                try:
                    result = subprocess.run(
                        [str(python_exe), '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    version_output = result.stdout.strip() or result.stderr.strip()
                    major, minor = python_version.split('.')[:2]
                    expected_version = f"{major}.{minor}"
                    
                    if expected_version in version_output:
                        if not quiet:
                            print(f"Окружение {env_name} уже существует с правильной версией Python")
                        return env_dir
                    else:
                        if not quiet:
                            print(f"Окружение {env_name} существует, но версия Python не совпадает!")
                            print(f"Ожидалось: {expected_version}, найдено: {version_output}")
                            print(f"Пересоздаю окружение...")
                        force_recreate = True
                except Exception as e:
                    if not quiet:
                        print(f"Не удалось проверить версию Python в окружении: {e}")
                        print(f"Пересоздаю окружение...")
                    force_recreate = True
            
            if force_recreate and not quiet:
                print(f"Удаление старого окружения {env_name}...")
                shutil.rmtree(env_dir)
        
        # Устанавливаем Python если нужно (пробуем все методы)
        try:
            python_path = self.python_installer.install_python(python_version, use_pyenv=True, quiet=quiet, offline=offline)
            if not python_path:
                raise RuntimeError(f"Не удалось установить Python {python_version}")
        except RuntimeError as e:
            # Передаем сообщение об ошибке дальше
            raise
        
        # Проверяем версию установленного Python
        try:
            result = subprocess.run(
                [str(python_path), '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_output = result.stdout.strip() or result.stderr.strip()
            parts = python_version.split('.')[:2]
            expected_version = f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else python_version
            # Для PyPy: "Python 3.11.0 (pypy3.11-...)" содержит expected
            if expected_version not in version_output:
                raise RuntimeError(
                    f"Версия установленного Python не совпадает! "
                    f"Ожидалось: {expected_version}, получено: {version_output}. "
                    f"Установите Python {python_version} в систему."
                )
        except RuntimeError:
            raise
        except Exception as e:
            if not quiet and "Версия установленного Python" not in str(e):
                print(f"Предупреждение: не удалось проверить версию Python: {e}")
        
        if not quiet:
            print(f"Создание виртуального окружения {env_name} с Python {python_version}...")
        
        # Создаем виртуальное окружение
        try:
            # Используем venv для Python 3 / PyPy3 или virtualenv для Python 2 / PyPy2
            is_python2 = python_version.startswith('2') or 'pypy2' in python_version.lower()
            if is_python2:
                # Для Python 2 / PyPy2 используем virtualenv
                self._create_virtualenv_python2(python_path, env_dir)
            else:
                # Для Python 3 / PyPy3 используем venv
                self._create_venv_python3(python_path, env_dir)
            
            # Проверяем версию Python в созданном окружении
            python_exe = self.get_python_executable(env_dir)
            if python_exe.exists():
                try:
                    # Для bat файлов на Windows используем cmd /c
                    if python_exe.suffix == '.bat' and os.name == 'nt':
                        cmd = ['cmd', '/c', str(python_exe), '--version']
                    else:
                        cmd = [str(python_exe), '--version']
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=env_dir.parent
                    )
                    version_output = result.stdout.strip() or result.stderr.strip()
                    major, minor = python_version.split('.')[:2]
                    expected_version = f"{major}.{minor}"
                    
                    if version_output and expected_version in version_output:
                        if not quiet:
                            print(f"Версия Python проверена: {version_output}")
                    elif version_output and not quiet:
                        print(f"Предупреждение: версия Python может не совпадать. Получено: {version_output}")
                    elif not quiet:
                        print(f"Предупреждение: не удалось получить версию Python из {python_exe}")
                        print(f"Продолжаем с предположением, что версия правильная...")
                except Exception as e:
                    if not quiet:
                        print(f"Предупреждение: не удалось проверить версию Python: {e}")
                        print(f"Продолжаем с предположением, что версия правильная...")
            
            if not quiet:
                print(f"Окружение {env_name} создано успешно")
            return env_dir
            
        except Exception as e:
            # Удаляем частично созданное окружение
            if env_dir.exists():
                shutil.rmtree(env_dir)
            raise RuntimeError(f"Ошибка при создании окружения: {e}")
    
    def _create_venv_python3(self, python_path: Path, env_dir: Path):
        """Создает venv окружение для Python 3."""
        # Проверяем, поддерживает ли Python модуль venv
        try:
            result = subprocess.run(
                [str(python_path), '-m', 'venv', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                # Если venv не поддерживается (например, embeddable версия), создаем простое окружение
                print("Модуль venv не поддерживается, создаем простое окружение...")
                self._create_simple_env(python_path, env_dir)
                return
        except Exception:
            # Если проверка не удалась, пробуем создать venv
            pass
        
        # Пытаемся создать venv
        try:
            result = subprocess.run(
                [str(python_path), '-m', 'venv', str(env_dir)],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            # Если venv не работает (например, embeddable версия), создаем простое окружение
            print(f"Не удалось создать venv: {e.stderr if e.stderr else 'неизвестная ошибка'}")
            print("Создаем простое окружение...")
            self._create_simple_env(python_path, env_dir)
    
    def _create_virtualenv_python2(self, python_path: Path, env_dir: Path):
        """Создает virtualenv окружение для Python 2."""
        # Пытаемся использовать virtualenv если доступен
        try:
            result = subprocess.run(
                [str(python_path), '-m', 'virtualenv', str(env_dir)],
                capture_output=True,
                text=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Если virtualenv недоступен, создаем простое окружение вручную
            self._create_simple_env(python_path, env_dir)
    
    def _create_simple_env(self, python_path: Path, env_dir: Path):
        """Создает простое окружение без virtualenv (для Python 2)."""
        env_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем структуру директорий
        bin_dir = env_dir / 'bin' if os.name != 'nt' else env_dir / 'Scripts'
        lib_dir = env_dir / 'lib'
        
        bin_dir.mkdir(parents=True, exist_ok=True)
        lib_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем символическую ссылку или копию Python
        system = os.name
        if system == 'nt':  # Windows
            target_python = bin_dir / 'python.exe'
            target_bat = bin_dir / 'python.bat'
            
            # Определяем исходную директорию Python
            original_python_path = python_path
            python_dir = None
            
            if python_path.is_dir():
                python_dir = python_path
                potential_python = python_path / 'python.exe'
                if potential_python.exists():
                    python_path = potential_python
                else:
                    # Ищем в поддиректориях (для embeddable версий)
                    for subdir in python_path.iterdir():
                        if subdir.is_dir():
                            potential_python = subdir / 'python.exe'
                            if potential_python.exists():
                                python_path = potential_python
                                python_dir = subdir
                                break
            elif python_path.exists() and python_path.suffix == '.exe':
                python_dir = python_path.parent
            
            # Для Windows создаем bat файл, который вызывает исходный Python
            # Это более надежно, чем копировать файлы
            if python_path.exists():
                # Создаем bat файл который вызывает исходный Python
                bat_content = f'@echo off\n"{python_path}" %*\n'
                with open(target_bat, 'w', encoding='utf-8') as f:
                    f.write(bat_content)
                
                # Также создаем python.exe как bat (для совместимости)
                # Но лучше использовать bat напрямую
                print(f"Создан bat файл для Python: {target_bat}")
                print(f"Используется Python: {python_path}")
                
                # Копируем pip если доступен
                try:
                    if python_dir:
                        pip_locations = [
                            python_dir / 'Scripts' / 'pip.exe',
                            python_dir.parent / 'Scripts' / 'pip.exe' if python_dir.parent.exists() else None,
                        ]
                    else:
                        pip_locations = [
                            python_path.parent / 'Scripts' / 'pip.exe',
                            python_path.parent.parent / 'Scripts' / 'pip.exe' if python_path.parent.parent.exists() else None,
                        ]
                    
                    for pip_path in pip_locations:
                        if pip_path and pip_path.exists():
                            # Создаем bat для pip тоже
                            pip_bat = bin_dir / 'pip.bat'
                            pip_bat_content = f'@echo off\n"{pip_path}" %*\n'
                            with open(pip_bat, 'w', encoding='utf-8') as f:
                                f.write(pip_bat_content)
                            print(f"pip доступен через: {pip_bat}")
                            break
                except Exception as e:
                    print(f"Не удалось настроить pip: {e}")
            else:
                # Если Python не найден, создаем bat который вызывает системный
                actual_python = original_python_path if original_python_path.exists() else python_path
                bat_content = f'@echo off\n"{actual_python}" %*\n'
                with open(target_bat, 'w', encoding='utf-8') as f:
                    f.write(bat_content)
                print(f"Создан bat файл для Python: {target_bat}")
        else:  # Unix-like
            # Создаем символическую ссылку
            python_link = bin_dir / 'python'
            if python_link.exists():
                python_link.unlink()
            try:
                python_link.symlink_to(python_path)
            except OSError:
                # Если симлинк не работает, копируем
                shutil.copy2(python_path, python_link)
    
    def get_python_executable(self, env_dir: Path) -> Path:
        """
        Возвращает путь к исполняемому файлу Python в окружении.
        
        Args:
            env_dir: Директория окружения
            
        Returns:
            Path к python.exe/python или python.bat
        """
        system = os.name
        if system == 'nt':  # Windows
            # Сначала проверяем bat файл (более надежно для Python 2)
            bat_file = env_dir / 'Scripts' / 'python.bat'
            if bat_file.exists():
                return bat_file
            # Затем проверяем exe
            exe_file = env_dir / 'Scripts' / 'python.exe'
            if exe_file.exists():
                return exe_file
            # Если ничего не найдено, возвращаем bat (будет создан при необходимости)
            return bat_file
        else:  # Unix-like
            return env_dir / 'bin' / 'python'
    
    def install_requirements(self, env_dir: Path, requirements_path: str, quiet: bool = False) -> bool:
        """
        Устанавливает зависимости из requirements.txt в окружение.
        
        Args:
            env_dir: Директория окружения
            requirements_path: Путь к requirements.txt
            
        Returns:
            True если установка успешна
        """
        python_exe = self.get_python_executable(env_dir)
        
        if not python_exe.exists():
            raise RuntimeError(f"Python не найден в окружении: {env_dir}")
        
        if not quiet:
            print(f"Установка зависимостей из {requirements_path}...")
        
        try:
            # Проверяем наличие pip
            result = subprocess.run(
                [str(python_exe), '-m', 'pip', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                print("pip не доступен, пытаемся установить...")
                # Пытаемся установить pip
                self._install_pip(python_exe)
            
            # Устанавливаем зависимости
            result = subprocess.run(
                [str(python_exe), '-m', 'pip', 'install', '-r', requirements_path],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                if not quiet:
                    print("Зависимости установлены успешно")
                return True
            else:
                print(f"Ошибка при установке зависимостей: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Ошибка при установке зависимостей: {e}")
            return False
    
    def _install_pip(self, python_exe: Path):
        """Устанавливает pip в окружение."""
        try:
            # Скачиваем get-pip.py
            import urllib.request
            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_path = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
            urllib.request.urlretrieve(get_pip_url, get_pip_path.name)
            
            # Запускаем get-pip.py
            subprocess.run(
                [str(python_exe), get_pip_path.name],
                check=True
            )
            
            # Удаляем временный файл
            os.unlink(get_pip_path.name)
            
        except Exception as e:
            print(f"Не удалось установить pip: {e}")
    
    def run_script(
        self,
        script_path: str,
        python_version: str,
        args: Optional[List[str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        requirements_path: Optional[str] = None,
        encoding: Optional[str] = None,
        no_deps: bool = False,
        work_dir: Optional[str] = None,
        script_display_name: Optional[str] = None,
        log_file: Optional[str] = None,
        quiet: bool = False,
        offline: bool = False,
        config_interpreter_opts: Optional[Dict[str, str]] = None
    ) -> int:
        """
        Запускает Python скрипт в изолированном окружении.
        
        Args:
            script_path: Путь к Python скрипту
            python_version: Версия Python
            args: Аргументы для скрипта
            env_vars: Переменные окружения
            requirements_path: Путь к requirements.txt
            encoding: Кодировка для запуска скрипта (например, utf-8, cp1251)
            no_deps: Не устанавливать зависимости из requirements.txt
            work_dir: Рабочая директория (по умолчанию — директория скрипта)
            script_display_name: Имя для отображения (например, notebook.ipynb вместо temp-файла)
            log_file: Путь к файлу для записи вывода (stdout и stderr)
            quiet: Скрыть служебные сообщения
            
        Returns:
            Код возврата скрипта
        """
        script_path = Path(script_path).absolute()
        
        # Jython: запуск через java -jar (без venv)
        if alternative_interpreters.is_alternative_interpreter(python_version) == 'jython':
            if not alternative_interpreters.java_available():
                raise RuntimeError("Jython требует Java. Установите Java (java -version) и повторите.")
            jar_path = self.python_installer.install_python(python_version, use_pyenv=False, quiet=quiet, offline=offline)
            if not jar_path or not jar_path.exists():
                raise RuntimeError("Jython не установлен. Убедитесь, что Java установлена (java -version).")
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            if encoding:
                env['PYTHONIOENCODING'] = f"{encoding}:replace"
            cwd = Path(work_dir) if work_dir else script_path.parent
            
            # Установка зависимостей для Jython: java -jar jython.jar -m pip install -r requirements.txt
            if requirements_path and not no_deps:
                req_path = Path(requirements_path)
                if not req_path.is_absolute():
                    if not req_path.exists():
                        req_path = script_path.parent / req_path
                    if not req_path.exists():
                        req_path = Path.cwd() / req_path
                if not req_path.exists():
                    raise FileNotFoundError(f"Файл requirements не найден: {requirements_path}")
                if not quiet:
                    print(f"Установка зависимостей из {req_path} для Jython...")
                java_opts_str = (config_interpreter_opts or {}).get('java_opts') or ''
                java_args = java_opts_str.split() if java_opts_str else []
                pip_cmd = ['java'] + java_args + ['-jar', str(jar_path), '-m', 'pip', 'install', '-r', str(req_path)]
                subprocess.run(pip_cmd, env=env, cwd=str(cwd), capture_output=quiet)
            
            java_opts = (config_interpreter_opts or {}).get('java_opts') or os.environ.get('JAVA_OPTS', '')
            java_args = java_opts.split() if java_opts else []
            cmd = ['java'] + java_args + ['-jar', str(jar_path), str(script_path)]
            if args:
                cmd.extend(args)
            if not quiet:
                print(f"Запуск скрипта через Jython (Java)...")
            
            # Поддержка --log-file
            log_stream = None
            if log_file:
                log_path = Path(log_file)
                if not log_path.is_absolute():
                    log_path = cwd / log_path
                log_stream = open(log_path, 'w', encoding='utf-8', errors='replace')
                result = subprocess.run(cmd, env=env, cwd=str(cwd), stdout=log_stream, stderr=subprocess.STDOUT)
                log_stream.close()
                if not quiet:
                    print(f"Вывод сохранён в {log_path}")
            else:
                result = subprocess.run(cmd, env=env, cwd=str(cwd))
            return result.returncode
        
        # Создаем или получаем окружение (без пересоздания, так как это уже сделано)
        env_dir = self.create_environment(python_version, force_recreate=False, quiet=quiet, offline=offline)
        python_exe = self.get_python_executable(env_dir)
        
        # Проверяем, что Python существует
        if not python_exe.exists():
            raise RuntimeError(f"Python не найден в окружении: {env_dir}")
        
        # Формируем команду с учетом типа файла
        if python_exe.suffix == '.bat' and os.name == 'nt':
            # Для bat файлов на Windows используем cmd /c
            base_cmd = ['cmd', '/c', str(python_exe)]
        else:
            base_cmd = [str(python_exe)]
        
        # Для Python 2 с нестандартной кодировкой нужно убедиться, что файл читается правильно
        # Python сам читает файл с кодировкой из комментария, но если файл сохранен в другой кодировке,
        # может быть проблема. Устанавливаем переменную окружения для декодирования исходного кода
        if encoding and python_version.startswith('2'):
            # Python 2 использует кодировку из комментария coding, но можно переопределить через переменную
            # Однако это не всегда работает, поэтому полагаемся на комментарий в файле
            pass
        
        # Проверяем версию Python перед запуском (опционально)
        try:
            version_cmd = base_cmd + ['--version']
            result = subprocess.run(
                version_cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=script_path.parent
            )
            version_output = result.stdout.strip() or result.stderr.strip()
            if version_output:
                major, minor = python_version.split('.')[:2]
                expected_version = f"{major}.{minor}"
                if expected_version in version_output:
                    if not quiet:
                        print(f"Версия Python подтверждена: {version_output}")
                elif not quiet:
                    print(f"Предупреждение: версия может не совпадать. Получено: {version_output}")
        except Exception as e:
            if not quiet:
                print(f"Не удалось проверить версию Python: {e}")
                print(f"Продолжаем выполнение...")
        
        # Устанавливаем зависимости если нужно (пропускаем при --no-deps)
        if requirements_path and not no_deps and not quiet:
            # Преобразуем относительный путь в абсолютный
            requirements_path = Path(requirements_path)
            if not requirements_path.is_absolute():
                # Если путь относительный, ищем относительно текущей директории или директории скрипта
                if not requirements_path.exists():
                    # Пробуем относительно директории скрипта
                    requirements_path = script_path.parent / requirements_path
                if not requirements_path.exists():
                    # Пробуем относительно текущей директории
                    requirements_path = Path.cwd() / requirements_path
                if not requirements_path.exists():
                    raise FileNotFoundError(f"Файл requirements.txt не найден: {requirements_path}")
            
            self.install_requirements(env_dir, str(requirements_path), quiet=quiet)
        
        # Подготавливаем переменные окружения
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        # PyPy: PYPY_JIT_OPTIONS из конфига
        if alternative_interpreters.is_alternative_interpreter(python_version) == 'pypy':
            pypy_opts = (config_interpreter_opts or {}).get('pypy_jit_options') or os.environ.get('PYPY_JIT_OPTIONS', '')
            if pypy_opts:
                env['PYPY_JIT_OPTIONS'] = pypy_opts
        
        # Устанавливаем кодировку если указана
        if encoding:
            # Для Python 2 используем PYTHONIOENCODING для ввода/вывода
            # Также устанавливаем PYTHONIOENCODING для декодирования исходного кода (если поддерживается)
            if python_version.startswith('2'):
                # Python 2: используем формат encoding:errors для ввода/вывода
                env['PYTHONIOENCODING'] = f"{encoding}:replace"
                # Для Python 2.5+ можно использовать переменную для декодирования исходного кода
                # Но это работает только если файл правильно сохранен
            else:
                # Для Python 3 используем PYTHONIOENCODING и PYTHONUTF8
                env['PYTHONIOENCODING'] = f"{encoding}:replace"
                # Также можно использовать параметр -X utf8 для Python 3.7+
                if 'utf' in encoding.lower() or encoding.lower() == 'utf-8':
                    env['PYTHONUTF8'] = '1'
            if not quiet:
                print(f"Используется кодировка: {encoding}")
        
        # Также устанавливаем кодировку для консоли Windows
        if os.name == 'nt' and encoding:
            # Для Windows консоли устанавливаем кодовую страницу
            try:
                encoding_map = {
                    'utf-8': '65001',
                    'cp1251': '1251',
                    'cp866': '866',
                    'latin1': '1252',
                }
                codepage = encoding_map.get(encoding.lower())
                if codepage:
                    # Устанавливаем кодовую страницу консоли
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    kernel32.SetConsoleCP(int(codepage))
                    kernel32.SetConsoleOutputCP(int(codepage))
            except Exception:
                pass  # Игнорируем ошибки установки кодовой страницы
        
        # Формируем команду
        cmd = base_cmd + [str(script_path)]
        if args:
            cmd.extend(args)
        
        # Рабочая директория
        cwd = Path(work_dir) if work_dir else script_path.parent
        
        display_name = script_display_name or script_path.name
        
        log_stream = None
        old_stdout = old_stderr = None
        if log_file:
            log_path = Path(log_file)
            if not log_path.is_absolute():
                log_path = cwd / log_path
            log_stream = open(log_path, 'w', encoding='utf-8', errors='replace')
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = log_stream
            if not quiet:
                print(f"Лог: {log_path}", file=old_stdout)
        
        if not quiet:
            print(f"Запуск скрипта {display_name} в Python {python_version}...")
            print(f"Используется Python: {python_exe}")
        
        try:
            kwargs = {
                'env': env,
                'cwd': str(cwd),
                'check': False
            }
            
            script_has_input = self._check_interactive_input(script_path, encoding)
            
            if log_stream:
                kwargs['stdin'] = sys.stdin
                kwargs['stdout'] = sys.stdout
                kwargs['stderr'] = sys.stderr
            elif script_has_input:
                kwargs['stdin'] = sys.stdin
                kwargs['stdout'] = sys.stdout
                kwargs['stderr'] = sys.stderr
            else:
                if encoding:
                    kwargs['encoding'] = encoding
                    kwargs['errors'] = 'replace'
            
            result = subprocess.run(
                cmd,
                **kwargs
            )
            if log_stream:
                sys.stdout, sys.stderr = old_stdout, old_stderr
                log_stream.close()
                if old_stdout and not quiet:
                    print(f"Вывод сохранён в {log_path}", file=old_stdout)
            return result.returncode
            
        except Exception as e:
            if log_stream:
                sys.stdout, sys.stderr = old_stdout, old_stderr
                log_stream.close()
            print(f"Ошибка при запуске скрипта: {e}")
            raise
    
    def _check_interactive_input(self, script_path: Path, encoding: Optional[str] = None) -> bool:
        """
        Проверяет, содержит ли скрипт интерактивный ввод (raw_input/input).
        
        Args:
            script_path: Путь к скрипту
            encoding: Кодировка файла (для правильного чтения)
            
        Returns:
            True если скрипт содержит интерактивный ввод
        """
        try:
            # Читаем файл с правильной кодировкой
            encodings_to_try = [encoding, 'utf-8', 'cp1251', 'latin1'] if encoding else ['utf-8', 'cp1251', 'latin1']
            
            content = None
            for enc in encodings_to_try:
                if not enc:
                    continue
                try:
                    with open(script_path, 'r', encoding=enc, errors='ignore') as f:
                        content = f.read()
                        break
                except:
                    continue
            
            if content is None:
                # В крайнем случае используем latin1
                with open(script_path, 'r', encoding='latin1', errors='ignore') as f:
                    content = f.read()
            
            # Ищем вызовы raw_input или input
            return 'raw_input' in content or ('input(' in content and 'input(' not in content.replace('raw_input', ''))
        except:
            return False
    
    def run_shell(self, python_version: str, cwd: Optional[str] = None, quiet: bool = False, offline: bool = False) -> int:
        """
        Запускает интерактивную оболочку Python в окружении.
        
        Args:
            python_version: Версия Python (включая pypy3.11, jython)
            cwd: Рабочая директория (по умолчанию текущая)
            offline: Режим offline
            
        Returns:
            Код возврата
        """
        # Jython: java -jar jython.jar
        if alternative_interpreters.is_alternative_interpreter(python_version) == 'jython':
            if not alternative_interpreters.java_available():
                raise RuntimeError("Jython требует Java. Установите Java (java -version) и повторите.")
            jar_path = self.python_installer.install_python(python_version, use_pyenv=False, quiet=quiet, offline=offline)
            if not jar_path or not jar_path.exists():
                raise RuntimeError("Jython не установлен. Убедитесь, что Java установлена.")
            work_dir = Path(cwd) if cwd else Path.cwd()
            if not quiet:
                print(f"Запуск Jython shell в {work_dir}...")
            return subprocess.call(['java', '-jar', str(jar_path)], cwd=str(work_dir))
        
        env_dir = self.create_environment(python_version, force_recreate=False, quiet=quiet, offline=offline)
        python_exe = self.get_python_executable(env_dir)
        
        if not python_exe.exists():
            raise RuntimeError(f"Python не найден в окружении: {env_dir}")
        
        work_dir = Path(cwd) if cwd else Path.cwd()
        work_dir = work_dir.resolve()
        
        if python_exe.suffix == '.bat' and os.name == 'nt':
            cmd = ['cmd', '/c', str(python_exe), '-i']
        else:
            cmd = [str(python_exe), '-i']
        
        if not quiet:
            print(f"Запуск Python shell ({python_version}) в {work_dir}...")
            print(f"Используется: {python_exe}")
            print("(Введите exit() для выхода)\n")
        
        return subprocess.call(cmd, cwd=str(work_dir))