"""Модуль для скачивания и установки различных версий Python."""

import os
import sys
import platform
import subprocess
import urllib.request
import urllib.error
import zipfile
import tarfile
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple
# Импортируем pyenv_manager только при необходимости, чтобы избежать циклических импортов


class PythonInstaller:
    """Управляет скачиванием и установкой различных версий Python."""
    
    # Базовые URL для скачивания Python
    PYTHON_ORG_BASE = "https://www.python.org/ftp/python"
    
    def __init__(self, install_dir: Optional[str] = None):
        """
        Инициализирует установщик Python.
        
        Args:
            install_dir: Директория для установки версий Python (по умолчанию ~/.pythondocker/python)
        """
        if install_dir is None:
            home_dir = Path.home()
            install_dir = home_dir / '.pythondocker' / 'python'
        
        self.install_dir = Path(install_dir)
        self.install_dir.mkdir(parents=True, exist_ok=True)
        self._pyenv_manager = None  # Ленивая инициализация
    
    def get_system_info(self) -> Tuple[str, str]:
        """
        Определяет информацию о системе.
        
        Returns:
            Tuple[str, str]: (платформа, архитектура)
        """
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == 'windows':
            if '64' in machine or machine == 'x86_64' or machine == 'amd64':
                return 'windows', 'amd64'
            return 'windows', 'win32'
        elif system == 'darwin':
            return 'macos', 'universal' if 'arm' in machine else 'x86_64'
        elif system == 'linux':
            if '64' in machine or machine == 'x86_64':
                return 'linux', 'x86_64'
            return 'linux', machine
        else:
            return system, machine
    
    def get_python_url(self, version: str) -> Optional[str]:
        """
        Формирует URL для скачивания Python.
        
        Args:
            version: Версия Python (например, '2.7.18', '3.11.0')
            
        Returns:
            URL для скачивания или None если версия не поддерживается
        """
        system, arch = self.get_system_info()
        major, minor = version.split('.')[:2]
        
        # Для Windows используем разные источники
        if system == 'windows':
            if major == '2':
                # Python 2.7 для Windows - используем MSI установщик или портативную версию
                if version.startswith('2.7'):
                    # Нормализуем до полной версии (2.7 -> 2.7.18)
                    version_full = '2.7.18' if version == '2.7' else version
                    # Пробуем MSI установщик
                    return f"{self.PYTHON_ORG_BASE}/{version_full}/python-{version_full}.msi"
            else:
                # Python 3.x для Windows
                # Пробуем сначала найти системный Python, так как embeddable не поддерживает venv
                # Если системный не найден, используем embeddable версию
                # Нормализуем версию до полной (например, 3.11 -> 3.11.0)
                if len(version.split('.')) == 2:
                    version_full = f"{version}.0"
                else:
                    version_full = version
                # Возвращаем embeddable версию, но предпочтительнее использовать системный Python
                return f"{self.PYTHON_ORG_BASE}/{version_full}/python-{version_full}-embed-{arch}.zip"
        
        # Для Linux и macOS используем исходники или бинарники
        elif system == 'linux':
            # Используем pyenv или скачиваем исходники
            return f"{self.PYTHON_ORG_BASE}/{version}/Python-{version}.tgz"
        
        elif system == 'darwin':
            return f"{self.PYTHON_ORG_BASE}/{version}/python-{version}-macos11.pkg"
        
        return None
    
    def python_installed(self, version: str) -> bool:
        """
        Проверяет, установлена ли версия Python.
        
        Args:
            version: Версия Python
            
        Returns:
            True если версия установлена
        """
        python_path = self.get_python_path(version)
        if python_path and python_path.exists():
            # Проверяем, что это действительно Python нужной версии
            try:
                result = subprocess.run(
                    [str(python_path), '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                installed_version = result.stdout.strip() or result.stderr.strip()
                return version in installed_version or version.split('.')[:2] == installed_version.split()[-1].split('.')[:2]
            except:
                return False
        return False
    
    def get_python_path(self, version: str) -> Optional[Path]:
        """
        Возвращает путь к исполняемому файлу Python.
        
        Args:
            version: Версия Python
            
        Returns:
            Path к python.exe/python или None
        """
        version_dir = self.install_dir / version
        system = platform.system().lower()
        
        if system == 'windows':
            python_exe = version_dir / 'python.exe'
        else:
            python_exe = version_dir / 'bin' / 'python'
        
        if python_exe.exists():
            return python_exe
        
        # Проверяем альтернативные пути
        if system == 'windows':
            # Для embeddable версий
            python_exe = version_dir / 'python.exe'
            if python_exe.exists():
                return python_exe
        
        return None
    
    def download_and_install_python(self, version: str) -> bool:
        """
        Скачивает и устанавливает версию Python.
        
        Args:
            version: Версия Python для скачивания
            
        Returns:
            True если установка успешна
        """
        url = self.get_python_url(version)
        if not url:
            return False
        
        system = platform.system().lower()
        version_dir = self.install_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Определяем расширение файла по URL
        if url.endswith('.msi'):
            # Установка через MSI на Windows
            return self._install_msi_python(url, version, version_dir)
        elif url.endswith('.zip'):
            # Распаковка embeddable версии
            return self._download_and_extract_zip(url, version, version_dir)
        elif url.endswith('.tgz') or url.endswith('.tar.gz'):
            # Распаковка исходников (требует компиляции)
            return self._download_and_extract_source(url, version, version_dir)
        else:
            return False
    
    def _install_msi_python(self, url: str, version: str, install_dir: Path) -> bool:
        """Устанавливает Python через MSI установщик на Windows."""
        system = platform.system().lower()
        if system != 'windows':
            return False
        
        print(f"Скачивание MSI установщика Python {version}...")
        
        # Скачиваем MSI во временную директорию
        with tempfile.NamedTemporaryFile(delete=False, suffix='.msi') as tmp_file:
            msi_path = Path(tmp_file.name)
        
        try:
            urllib.request.urlretrieve(url, msi_path)
            print(f"MSI установщик скачан: {msi_path}")
            
            # Устанавливаем MSI в тихом режиме в указанную директорию
            print(f"Установка Python {version} в {install_dir}...")
            
            # Используем msiexec для установки
            # /qn - тихая установка без UI
            # TARGETDIR - директория установки
            install_cmd = [
                'msiexec',
                '/i', str(msi_path),
                '/qn',  # Тихая установка
                f'TARGETDIR={install_dir}',
                'ADDLOCAL=ALL',
                '/L*v', str(install_dir / 'install.log')
            ]
            
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 минут на установку
            )
            
            if result.returncode == 0:
                # Ищем python.exe в установленной директории
                python_exe = install_dir / 'python.exe'
                if not python_exe.exists():
                    # Может быть в поддиректории
                    for subdir in install_dir.iterdir():
                        if subdir.is_dir():
                            potential_python = subdir / 'python.exe'
                            if potential_python.exists():
                                python_exe = potential_python
                                break
                
                if python_exe.exists():
                    print(f"Python {version} успешно установлен: {python_exe}")
                    return True
                else:
                    print(f"Python установлен, но python.exe не найден в {install_dir}")
                    return False
            else:
                print(f"Ошибка при установке MSI: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Ошибка при установке через MSI: {e}")
            return False
        finally:
            # Удаляем временный MSI файл
            if msi_path.exists():
                try:
                    msi_path.unlink()
                except:
                    pass
    
    def _download_and_extract_zip(self, url: str, version: str, extract_dir: Path) -> bool:
        """Скачивает и распаковывает embeddable версию Python (ZIP)."""
        download_path = extract_dir / f"python-{version}.zip"
        
        print(f"Скачивание Python {version} из {url}...")
        
        try:
            urllib.request.urlretrieve(url, download_path)
            print(f"Python {version} скачан успешно")
            
            # Распаковываем
            return self._extract_python(download_path, extract_dir, 'windows')
            
        except urllib.error.URLError as e:
            print(f"Ошибка при скачивании: {e}")
            return False
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return False
    
    def _download_and_extract_source(self, url: str, version: str, extract_dir: Path) -> bool:
        """Скачивает исходники Python (требует компиляции)."""
        download_path = extract_dir / f"Python-{version}.tgz"
        
        print(f"Скачивание исходников Python {version} из {url}...")
        print("ВНИМАНИЕ: Компиляция из исходников требует времени и инструментов разработки!")
        
        try:
            urllib.request.urlretrieve(url, download_path)
            print(f"Исходники Python {version} скачаны успешно")
            
            # Распаковываем
            if self._extract_python(download_path, extract_dir, 'linux'):
                print("Исходники распакованы. Требуется компиляция...")
                print("Для компиляции используйте pyenv или установите Python вручную.")
                return False  # Пока не компилируем автоматически
            
            return False
            
        except urllib.error.URLError as e:
            print(f"Ошибка при скачивании: {e}")
            return False
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return False
    
    def _extract_python(self, archive_path: Path, extract_dir: Path, system: str) -> bool:
        """
        Распаковывает архив Python.
        
        Args:
            archive_path: Путь к архиву
            extract_dir: Директория для распаковки
            system: Операционная система
            
        Returns:
            True если распаковка успешна
        """
        try:
            print(f"Распаковка Python в {extract_dir}...")
            
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif archive_path.suffix in ['.tgz', '.gz'] or archive_path.name.endswith('.tar.gz'):
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_dir)
                    # Для исходников нужно компилировать, но это сложно
                    # Пока используем системный Python или pyenv
            else:
                print(f"Неизвестный формат архива: {archive_path.suffix}")
                return False
            
            # Удаляем архив после распаковки
            archive_path.unlink()
            
            print(f"Python распакован успешно")
            return True
            
        except zipfile.BadZipFile:
            print(f"Ошибка: файл не является zip архивом. Возможно, это установщик MSI.")
            return False
        except Exception as e:
            print(f"Ошибка при распаковке: {e}")
            return False
    
    def install_python(self, version: str, use_pyenv: bool = True) -> Optional[Path]:
        """
        Устанавливает версию Python используя различные методы.
        
        Порядок попыток:
        1. Проверка уже установленной версии
        2. Поиск системного Python
        3. Установка через pyenv (если доступен)
        4. Скачивание и установка через MSI/embeddable (Windows)
        5. Скачивание исходников и компиляция (Linux/macOS)
        
        Args:
            version: Версия Python
            use_pyenv: Использовать pyenv если доступен
            
        Returns:
            Path к исполняемому файлу Python или None
            
        Raises:
            RuntimeError: Если Python нужной версии не найден и не может быть установлен
        """
        # Метод 1: Проверяем, установлена ли уже
        if self.python_installed(version):
            python_path = self.get_python_path(version)
            if python_path:
                print(f"Python {version} уже установлен: {python_path}")
                return python_path
        
        # Метод 2: Пытаемся использовать системный Python если версия совпадает
        # Для Python 3 предпочитаем системный Python, так как embeddable не поддерживает venv
        system_python = self._find_system_python(version)
        if system_python:
            # Проверяем версию еще раз для уверенности
            try:
                result = subprocess.run(
                    [str(system_python), '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version_output = result.stdout.strip() or result.stderr.strip()
                major, minor = version.split('.')[:2]
                expected_version = f"{major}.{minor}"
                
                if expected_version in version_output:
                    print(f"Используется системный Python {version}: {system_python}")
                    return system_python
                else:
                    print(f"Найден Python, но версия не совпадает: {version_output}")
            except Exception as e:
                print(f"Не удалось проверить версию найденного Python: {e}")
        
        # Метод 3: Пытаемся использовать pyenv
        if use_pyenv:
            if self._pyenv_manager is None:
                try:
                    from .pyenv_manager import PyenvManager
                    self._pyenv_manager = PyenvManager()
                except ImportError:
                    self._pyenv_manager = None
            
            if self._pyenv_manager and self._pyenv_manager.pyenv_available:
                print(f"Попытка установки Python {version} через pyenv...")
                # Нормализуем версию для pyenv (нужна полная версия)
                pyenv_version = self._normalize_version_for_pyenv(version)
                if pyenv_version:
                    if self._pyenv_manager.version_installed(pyenv_version):
                        python_path = self._pyenv_manager.get_python_path(pyenv_version)
                        if python_path:
                            print(f"Используется Python {version} из pyenv: {python_path}")
                            return python_path
                    else:
                        # Пытаемся установить через pyenv
                        if self._pyenv_manager.install_version(pyenv_version):
                            python_path = self._pyenv_manager.get_python_path(pyenv_version)
                            if python_path:
                                print(f"Python {version} установлен через pyenv: {python_path}")
                                return python_path
        
        # Метод 4: Скачиваем и устанавливаем автоматически
        if self.download_and_install_python(version):
            python_path = self.get_python_path(version)
            if python_path and python_path.exists():
                return python_path
        
        # Если не удалось найти или установить нужную версию
        raise RuntimeError(
            f"Python {version} не найден и не может быть установлен автоматически.\n"
            f"\nПопробуйте один из следующих способов:\n"
            f"1. Установите Python {version} вручную:\n"
            f"   - Windows: https://www.python.org/downloads/\n"
            f"   - Linux: используйте пакетный менеджер (apt, yum, etc.)\n"
            f"   - macOS: brew install python@{version}\n"
            f"2. Установите pyenv и используйте: pyenv install {version}\n"
            f"3. Используйте Python Launcher (Windows): py -{version.split('.')[0]}.{version.split('.')[1]} --version"
        )
    
    def _normalize_version_for_pyenv(self, version: str) -> Optional[str]:
        """Нормализует версию для pyenv (нужна полная версия)."""
        parts = version.split('.')
        if len(parts) >= 2:
            major, minor = parts[0], parts[1]
            # Для pyenv нужна полная версия, пробуем найти последнюю патч-версию
            # Для Python 2.7 это обычно 2.7.18
            if major == '2' and minor == '7':
                return '2.7.18'
            # Для других версий возвращаем как есть или пробуем найти последнюю
            if len(parts) == 2:
                # Пытаемся найти последнюю версию через pyenv
                return None  # pyenv сам найдет последнюю версию
            return version
        return None
    
    def _find_system_python(self, version: str) -> Optional[Path]:
        """
        Ищет системный Python нужной версии.
        
        Args:
            version: Версия Python
            
        Returns:
            Path к Python или None
        """
        major, minor = version.split('.')[:2]
        target_version = f"{major}.{minor}"
        
        # Проверяем текущий Python только если версия совпадает
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if current_version == target_version:
            python_path = Path(sys.executable)
            # Проверяем версию еще раз для уверенности
            try:
                result = subprocess.run(
                    [str(python_path), '--version'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                version_output = result.stdout.strip() or result.stderr.strip()
                if target_version in version_output:
                    return python_path
            except:
                pass
        
        # Пытаемся найти python{major}.{minor} в PATH
        system = platform.system().lower()
        python_names = [
            f"python{major}.{minor}",
            f"python{major}{minor}",
        ]
        
        if system == 'windows':
            python_names.extend([
                f"python{major}.{minor}.exe",
                f"python{major}{minor}.exe",
            ])
        
        # Сначала пробуем Python Launcher для Windows
        if system == 'windows':
            try:
                # Пробуем разные варианты версий для py launcher
                version_variants = [
                    f'-{major}.{minor}',
                    f'-{major}{minor}',
                    f'-{major}.{minor}.0',
                ]
                
                for version_flag in version_variants:
                    try:
                        result = subprocess.run(
                            ['py', version_flag, '--version'],
                            capture_output=True,
                            text=True,
                            timeout=3
                        )
                        if result.returncode == 0:
                            version_output = result.stdout.strip() or result.stderr.strip()
                            if target_version in version_output:
                                # Получаем путь через py launcher
                                result2 = subprocess.run(
                                    ['py', version_flag, '-c', 'import sys; print(sys.executable)'],
                                    capture_output=True,
                                    text=True,
                                    timeout=3
                                )
                                if result2.returncode == 0:
                                    python_path = Path(result2.stdout.strip())
                                    if python_path.exists():
                                        # Проверяем версию еще раз
                                        result3 = subprocess.run(
                                            [str(python_path), '--version'],
                                            capture_output=True,
                                            text=True,
                                            timeout=3
                                        )
                                        version_output2 = result3.stdout.strip() or result3.stderr.strip()
                                        if target_version in version_output2:
                                            return python_path
                    except Exception:
                        continue
            except Exception:
                pass
        
        # Ищем в PATH
        for name in python_names:
            if name:
                try:
                    result = subprocess.run(
                        ['where' if system == 'windows' else 'which', name],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        paths = [p.strip() for p in result.stdout.strip().split('\n') if p.strip()]
                        for path_str in paths:
                            python_path = Path(path_str)
                            if python_path.exists():
                                # Проверяем версию
                                try:
                                    result2 = subprocess.run(
                                        [str(python_path), '--version'],
                                        capture_output=True,
                                        text=True,
                                        timeout=2
                                    )
                                    version_output = result2.stdout.strip() or result2.stderr.strip()
                                    if target_version in version_output:
                                        return python_path
                                except Exception:
                                    continue
                except Exception:
                    continue
        
        return None
