"""Модуль для создания и управления изолированными окружениями Python."""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict
from .python_installer import PythonInstaller


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
    
    def create_environment(self, python_version: str, env_name: Optional[str] = None, force_recreate: bool = False) -> Path:
        """
        Создает изолированное виртуальное окружение.
        
        Args:
            python_version: Версия Python (например, '2.7', '3.11')
            env_name: Имя окружения (по умолчанию генерируется автоматически)
            force_recreate: Пересоздать окружение если оно уже существует
            
        Returns:
            Path к директории окружения
        """
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
                        print(f"Окружение {env_name} уже существует с правильной версией Python")
                        return env_dir
                    else:
                        print(f"Окружение {env_name} существует, но версия Python не совпадает!")
                        print(f"Ожидалось: {expected_version}, найдено: {version_output}")
                        print(f"Пересоздаю окружение...")
                        force_recreate = True
                except Exception as e:
                    print(f"Не удалось проверить версию Python в окружении: {e}")
                    print(f"Пересоздаю окружение...")
                    force_recreate = True
            
            if force_recreate:
                print(f"Удаление старого окружения {env_name}...")
                shutil.rmtree(env_dir)
        
        # Устанавливаем Python если нужно (пробуем все методы)
        try:
            python_path = self.python_installer.install_python(python_version, use_pyenv=True)
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
            major, minor = python_version.split('.')[:2]
            expected_version = f"{major}.{minor}"
            
            if expected_version not in version_output:
                raise RuntimeError(
                    f"Версия установленного Python не совпадает! "
                    f"Ожидалось: {expected_version}, получено: {version_output}. "
                    f"Установите Python {python_version} в систему."
                )
        except Exception as e:
            if "Версия установленного Python" not in str(e):
                print(f"Предупреждение: не удалось проверить версию Python: {e}")
        
        print(f"Создание виртуального окружения {env_name} с Python {python_version}...")
        
        # Создаем виртуальное окружение
        try:
            # Используем venv для Python 3.3+ или virtualenv для старых версий
            if python_version.startswith('2'):
                # Для Python 2 используем virtualenv
                self._create_virtualenv_python2(python_path, env_dir)
            else:
                # Для Python 3 используем venv
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
                        print(f"Версия Python проверена: {version_output}")
                    elif version_output:
                        print(f"Предупреждение: версия Python может не совпадать. Получено: {version_output}")
                        # Не выбрасываем ошибку, так как bat файл может работать правильно
                    else:
                        print(f"Предупреждение: не удалось получить версию Python из {python_exe}")
                        print(f"Продолжаем с предположением, что версия правильная...")
                except Exception as e:
                    print(f"Предупреждение: не удалось проверить версию Python: {e}")
                    print(f"Продолжаем с предположением, что версия правильная...")
            
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
    
    def install_requirements(self, env_dir: Path, requirements_path: str) -> bool:
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
        encoding: Optional[str] = None
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
            
        Returns:
            Код возврата скрипта
        """
        script_path = Path(script_path).absolute()
        
        # Создаем или получаем окружение (без пересоздания, так как это уже сделано)
        env_dir = self.create_environment(python_version, force_recreate=False)
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
                    print(f"Версия Python подтверждена: {version_output}")
                else:
                    print(f"Предупреждение: версия может не совпадать. Получено: {version_output}")
        except Exception as e:
            print(f"Не удалось проверить версию Python: {e}")
            print(f"Продолжаем выполнение...")
        
        # Устанавливаем зависимости если нужно
        if requirements_path:
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
            
            self.install_requirements(env_dir, str(requirements_path))
        
        # Подготавливаем переменные окружения
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
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
        
        print(f"Запуск скрипта {script_path.name} в Python {python_version}...")
        print(f"Используется Python: {python_exe}")
        
        try:
            # Настраиваем параметры для subprocess
            kwargs = {
                'env': env,
                'cwd': script_path.parent,
                'check': False
            }
            
            # Для интерактивных скриптов (с raw_input/input) нужно передавать stdin
            # Проверяем, есть ли в скрипте интерактивный ввод
            script_has_input = self._check_interactive_input(script_path, encoding)
            
            if script_has_input:
                # Передаем stdin/stdout/stderr напрямую для интерактивного ввода
                kwargs['stdin'] = sys.stdin
                kwargs['stdout'] = sys.stdout
                kwargs['stderr'] = sys.stderr
            else:
                # Для неинтерактивных скриптов можно использовать capture_output
                if encoding:
                    kwargs['encoding'] = encoding
                    kwargs['errors'] = 'replace'
            
            result = subprocess.run(
                cmd,
                **kwargs
            )
            return result.returncode
            
        except Exception as e:
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