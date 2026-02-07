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
import re
from pathlib import Path
from typing import Optional, Tuple, List

from . import alternative_interpreters
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
        
        Поддерживает любую версию Python, доступную на python.org.
        Автоматически находит доступные файлы для скачивания.
        
        Args:
            version: Версия Python (например, '2.3', '2.7.18', '3.11.0', '3.14')
            
        Returns:
            URL для скачивания (первый подходящий вариант)
        """
        system, arch = self.get_system_info()
        
        # Находим доступные версии на python.org
        available_versions = self._find_available_versions(version)
        
        if not available_versions:
            return None
        
        # Возвращаем URL для первой доступной версии
        # Проверка существования будет при скачивании
        for ver in available_versions:
            url = self._get_download_url_for_version(ver, system, arch)
            if url:
                return url
        
        return None
    
    def _find_available_versions(self, version: str) -> List[str]:
        """
        Находит доступные версии Python на python.org, соответствующие запрошенной версии.
        
        Args:
            version: Запрошенная версия (например, '2.3', '3.11', '3.14.1')
            
        Returns:
            Список доступных версий, отсортированных по убыванию
        """
        parts = version.split('.')
        
        # Если указана полная версия (X.Y.Z), возвращаем её
        if len(parts) >= 3:
            return [version]
        
        # Если указана короткая версия (X.Y), ищем все патч-версии
        if len(parts) == 2:
            major, minor = parts[0], parts[1]
            
            # Известные последние патч-версии (для быстрого доступа)
            known_versions = {
                '2.0': ['2.0.1', '2.0'],
                '2.1': ['2.1.3', '2.1.2', '2.1.1', '2.1'],
                '2.2': ['2.2.3', '2.2.2', '2.2.1', '2.2'],
                '2.3': ['2.3.7', '2.3.6', '2.3.5', '2.3.4', '2.3.3', '2.3.2', '2.3.1', '2.3'],
                '2.4': ['2.4.6', '2.4.5', '2.4.4', '2.4.3', '2.4.2', '2.4.1', '2.4'],
                '2.5': ['2.5.6', '2.5.5', '2.5.4', '2.5.3', '2.5.2', '2.5.1', '2.5'],
                '2.6': ['2.6.9', '2.6.8', '2.6.7', '2.6.6', '2.6.5', '2.6.4', '2.6.3', '2.6.2', '2.6.1', '2.6'],
                '2.7': ['2.7.18', '2.7.17', '2.7.16', '2.7.15', '2.7.14', '2.7.13', '2.7.12', '2.7.11', '2.7.10'],
                '3.0': ['3.0.1', '3.0'],
                '3.1': ['3.1.5', '3.1.4', '3.1.3', '3.1.2', '3.1.1', '3.1'],
                '3.2': ['3.2.6', '3.2.5', '3.2.4', '3.2.3', '3.2.2', '3.2.1', '3.2'],
                '3.3': ['3.3.7', '3.3.6', '3.3.5', '3.3.4', '3.3.3', '3.3.2', '3.3.1', '3.3.0'],
                '3.4': ['3.4.10', '3.4.9', '3.4.8', '3.4.7', '3.4.6', '3.4.5', '3.4.4', '3.4.3', '3.4.2', '3.4.1', '3.4.0'],
                '3.5': ['3.5.10', '3.5.9', '3.5.8', '3.5.7', '3.5.6', '3.5.5', '3.5.4', '3.5.3', '3.5.2', '3.5.1', '3.5.0'],
                '3.6': ['3.6.15', '3.6.14', '3.6.13', '3.6.12', '3.6.11', '3.6.10', '3.6.9', '3.6.8', '3.6.7', '3.6.6', '3.6.5', '3.6.4', '3.6.3', '3.6.2', '3.6.1', '3.6.0'],
                '3.7': ['3.7.17', '3.7.16', '3.7.15', '3.7.14', '3.7.13', '3.7.12', '3.7.11', '3.7.10', '3.7.9', '3.7.8', '3.7.7', '3.7.6', '3.7.5', '3.7.4', '3.7.3', '3.7.2', '3.7.1', '3.7.0'],
                '3.8': ['3.8.20', '3.8.19', '3.8.18', '3.8.17', '3.8.16', '3.8.15', '3.8.14', '3.8.13', '3.8.12', '3.8.11', '3.8.10', '3.8.9', '3.8.8', '3.8.7', '3.8.6', '3.8.5', '3.8.4', '3.8.3', '3.8.2', '3.8.1', '3.8.0'],
                '3.9': ['3.9.25', '3.9.24', '3.9.23', '3.9.22', '3.9.21', '3.9.20', '3.9.19', '3.9.18', '3.9.17', '3.9.16', '3.9.15', '3.9.14', '3.9.13', '3.9.12', '3.9.11', '3.9.10', '3.9.9', '3.9.8', '3.9.7', '3.9.6', '3.9.5', '3.9.4', '3.9.3', '3.9.2', '3.9.1', '3.9.0'],
                '3.10': ['3.10.19', '3.10.18', '3.10.17', '3.10.16', '3.10.15', '3.10.14', '3.10.13', '3.10.12', '3.10.11', '3.10.10', '3.10.9', '3.10.8', '3.10.7', '3.10.6', '3.10.5', '3.10.4', '3.10.3', '3.10.2', '3.10.1', '3.10.0'],
                '3.11': ['3.11.14', '3.11.13', '3.11.12', '3.11.11', '3.11.10', '3.11.9', '3.11.8', '3.11.7', '3.11.6', '3.11.5', '3.11.4', '3.11.3', '3.11.2', '3.11.1', '3.11.0'],
                '3.12': ['3.12.12', '3.12.11', '3.12.10', '3.12.9', '3.12.8', '3.12.7', '3.12.6', '3.12.5', '3.12.4', '3.12.3', '3.12.2', '3.12.1', '3.12.0'],
                '3.13': ['3.13.12', '3.13.11', '3.13.10', '3.13.9', '3.13.8', '3.13.7', '3.13.6', '3.13.5', '3.13.4', '3.13.3', '3.13.2', '3.13.1', '3.13.0'],
                '3.14': ['3.14.3', '3.14.2', '3.14.1', '3.14.0'],
                '3.15': ['3.15.0'],
            }
            
            version_key = f"{major}.{minor}"
            if version_key in known_versions:
                return known_versions[version_key]
            
            # Если версия не в списке, генерируем возможные варианты
            # Пробуем от .0 до .20
            versions = [f"{major}.{minor}.{patch}" for patch in range(20, -1, -1)]
            versions.insert(0, f"{major}.{minor}")  # Добавляем версию без патча
            return versions
        
        return [version]
    
    def _get_download_url_for_version(self, version: str, system: str, arch: str) -> Optional[str]:
        """
        Формирует URL для скачивания конкретной версии Python.
        
        Args:
            version: Полная версия Python
            system: Операционная система
            arch: Архитектура
            
        Returns:
            URL для скачивания
        """
        parts = version.split('.')
        major = parts[0] if parts else '3'
        
        if system == 'windows':
            if major == '2':
                # Python 2.x для Windows: MSI установщик
                return f"{self.PYTHON_ORG_BASE}/{version}/python-{version}.msi"
            else:
                # Python 3.x для Windows: embeddable версия
                return f"{self.PYTHON_ORG_BASE}/{version}/python-{version}-embed-{arch}.zip"
        
        elif system == 'linux':
            # Исходники для Linux
            return f"{self.PYTHON_ORG_BASE}/{version}/Python-{version}.tgz"
        
        elif system == 'darwin':
            # PKG для macOS
            return f"{self.PYTHON_ORG_BASE}/{version}/python-{version}-macos11.pkg"
        
        return None
    
    
    def python_installed(self, version: str) -> bool:
        """
        Проверяет, установлена ли версия Python.
        
        Args:
            version: Версия Python (включая pypy3.11, jython)
            
        Returns:
            True если версия установлена
        """
        # Альтернативные интерпретаторы
        alt = alternative_interpreters.is_alternative_interpreter(version)
        if alt == 'pypy':
            python_path = self.get_python_path(version)
        elif alt == 'jython':
            jar_path = alternative_interpreters.install_jython(self.install_dir, quiet=True)
            return jar_path is not None and jar_path.exists()
        else:
            python_path = self.get_python_path(version)
        if python_path and python_path.exists():
            # Для JAR (Jython) не проверяем --version
            if alt == 'jython' or (str(python_path).endswith('.jar')):
                return True
            try:
                result = subprocess.run(
                    [str(python_path), '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                installed_version = result.stdout.strip() or result.stderr.strip()
                if alt == 'pypy':
                    # PyPy: "Python 3.11.0 (pypy3.11-v7.3.20...)" — проверяем наличие версии
                    ver_part = version.replace('pypy', '')  # "3.11"
                    return ver_part in installed_version or version in installed_version
                parts = version.split('.')[:2]
                if len(parts) >= 2:
                    expected = f"{parts[0]}.{parts[1]}"
                    return version in installed_version or expected in installed_version
                return version in installed_version
            except Exception:
                return False
        return False
    
    def get_python_path(self, version: str) -> Optional[Path]:
        """
        Возвращает путь к исполняемому файлу Python.
        
        Args:
            version: Версия Python (включая pypy3.11, jython)
            
        Returns:
            Path к python.exe/python или jython.jar или None
        """
        # PyPy: путь к pypy/pypy3.exe или pypy/bin/pypy3
        alt = alternative_interpreters.is_alternative_interpreter(version)
        if alt == 'pypy':
            v_norm = version.lower().replace(' ', '')
            if not v_norm.startswith('pypy'):
                v_norm = 'pypy' + v_norm
            version_dir = self.install_dir / v_norm
            pypy_dir = version_dir / 'pypy'
            if pypy_dir.exists():
                system = platform.system().lower()
                if system == 'windows':
                    for name in ('pypy3.exe', 'python.exe', 'pypy.exe'):
                        exe = pypy_dir / name
                        if exe.exists():
                            return exe
                    for f in pypy_dir.rglob('pypy3.exe'):
                        return f
                else:
                    for p in (pypy_dir / 'bin' / 'pypy3', pypy_dir / 'bin' / 'python', pypy_dir / 'bin' / 'pypy'):
                        if p.exists():
                            return p
            return None
        if alt == 'jython':
            return alternative_interpreters.install_jython(self.install_dir, quiet=True)
        
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
    
    def download_and_install_python(self, version: str, quiet: bool = False) -> bool:
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
            return self._install_msi_python(url, version, version_dir, quiet=quiet)
        elif url.endswith('.zip'):
            return self._download_and_extract_zip(url, version, version_dir, quiet=quiet)
        elif url.endswith('.tgz') or url.endswith('.tar.gz'):
            return self._download_and_extract_source(url, version, version_dir, quiet=quiet)
        else:
            return False
    
    def _install_msi_python(self, url: str, version: str, install_dir: Path, quiet: bool = False) -> bool:
        """Устанавливает Python через MSI установщик на Windows."""
        system = platform.system().lower()
        if system != 'windows':
            return False
        
        if not quiet:
            print(f"Скачивание MSI установщика Python {version}...")
        
        # Скачиваем MSI во временную директорию
        with tempfile.NamedTemporaryFile(delete=False, suffix='.msi') as tmp_file:
            msi_path = Path(tmp_file.name)
        
        try:
            urllib.request.urlretrieve(url, msi_path)
            if not quiet:
                print(f"MSI установщик скачан: {msi_path}")
                print(f"Установка Python {version} в {install_dir}...")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                if not quiet:
                    print(f"MSI файл не найден (404), пробуем альтернативные версии...")
                return self._try_alternative_downloads(version, install_dir, quiet)
            print(f"Ошибка HTTP при скачивании MSI: {e}")
            return False
        except Exception as e:
            print(f"Ошибка при скачивании MSI: {e}")
            return False
        
        try:
            
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
                    if not quiet:
                        print(f"Python {version} успешно установлен: {python_exe}")
                    return True
                elif not quiet:
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
    
    def _download_and_extract_zip(self, url: str, version: str, extract_dir: Path, quiet: bool = False) -> bool:
        """Скачивает и распаковывает embeddable версию Python (ZIP)."""
        download_path = extract_dir / f"python-{version}.zip"
        
        if not quiet:
            print(f"Скачивание Python {version} из {url}...")
        
        try:
            urllib.request.urlretrieve(url, download_path)
            if not quiet:
                print(f"Python {version} скачан успешно")
            return self._extract_python(download_path, extract_dir, 'windows', quiet=quiet)
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Файл не найден, пробуем альтернативные версии
                if not quiet:
                    print(f"Файл не найден (404), пробуем альтернативные версии...")
                return self._try_alternative_downloads(version, extract_dir, quiet)
            print(f"Ошибка HTTP при скачивании: {e}")
            return False
        except urllib.error.URLError as e:
            print(f"Ошибка при скачивании: {e}")
            return False
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return False
    
    def _try_alternative_downloads(self, version: str, extract_dir: Path, quiet: bool = False) -> bool:
        """
        Пробует скачать альтернативные версии Python.
        
        Args:
            version: Версия Python
            extract_dir: Директория для установки
            quiet: Тихий режим
            
        Returns:
            True если удалось скачать
        """
        system, arch = self.get_system_info()
        available_versions = self._find_available_versions(version)
        
        # Пропускаем первую версию (она уже была попробована)
        for ver in available_versions[1:]:
            url = self._get_download_url_for_version(ver, system, arch)
            if not url:
                continue
            
            if not quiet:
                print(f"Пробую версию {ver}: {url}")
            
            try:
                if url.endswith('.zip'):
                    download_path = extract_dir / f"python-{ver}.zip"
                    urllib.request.urlretrieve(url, download_path)
                    if not quiet:
                        print(f"Python {ver} скачан успешно!")
                    return self._extract_python(download_path, extract_dir, 'windows', quiet=quiet)
                elif url.endswith('.msi'):
                    if not quiet:
                        print(f"Найден MSI установщик для версии {ver}")
                    return self._install_msi_python(url, ver, extract_dir, quiet=quiet)
            except urllib.error.HTTPError as e:
                if not quiet:
                    print(f"  Версия {ver} не найдена (HTTP {e.code})")
                continue
            except Exception as e:
                if not quiet:
                    print(f"  Ошибка при скачивании {ver}: {e}")
                continue
        
        return False
    
    def _download_and_extract_source(self, url: str, version: str, extract_dir: Path, quiet: bool = False) -> bool:
        """Скачивает исходники Python (требует компиляции)."""
        download_path = extract_dir / f"Python-{version}.tgz"
        
        print(f"Скачивание исходников Python {version} из {url}...")
        print("ВНИМАНИЕ: Компиляция из исходников требует времени и инструментов разработки!")
        
        try:
            urllib.request.urlretrieve(url, download_path)
            print(f"Исходники Python {version} скачаны успешно")
            
            if self._extract_python(download_path, extract_dir, 'linux', quiet=quiet):
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
    
    def _extract_python(self, archive_path: Path, extract_dir: Path, system: str, quiet: bool = False) -> bool:
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
            if not quiet:
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
            
            archive_path.unlink()
            if not quiet:
                print(f"Python распакован успешно")
            return True
            
        except zipfile.BadZipFile:
            print(f"Ошибка: файл не является zip архивом. Возможно, это установщик MSI.")
            return False
        except Exception as e:
            print(f"Ошибка при распаковке: {e}")
            return False
    
    def install_python(self, version: str, use_pyenv: bool = True, quiet: bool = False, offline: bool = False) -> Optional[Path]:
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
                if not quiet:
                    print(f"Python {version} уже установлен: {python_path}")
                return python_path
        
        # Альтернативные интерпретаторы (PyPy, Jython)
        alt = alternative_interpreters.is_alternative_interpreter(version)
        if alt == 'pypy':
            if offline:
                path = self.get_python_path(version)
                if path and path.exists():
                    return path
                raise RuntimeError(f"PyPy {version} не установлен. Режим --offline: установите вручную или запустите без --offline.")
            path = alternative_interpreters.install_pypy(version, self.install_dir, quiet=quiet)
            if path:
                return path
            raise RuntimeError(
                f"PyPy {version} не удалось установить. "
                f"Проверьте доступность https://downloads.python.org/pypy/"
            )
        if alt == 'jython':
            if offline:
                path = self.get_python_path(version)
                if path and path.exists():
                    return path
                raise RuntimeError("Jython не установлен. Режим --offline: установите вручную или запустите без --offline.")
            path = alternative_interpreters.install_jython(self.install_dir, quiet=quiet)
            if path:
                return path
            raise RuntimeError(
                "Jython не удалось установить. Убедитесь, что Java установлена (java -version)."
            )
        
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
                    if not quiet:
                        print(f"Используется системный Python {version}: {system_python}")
                    return system_python
                elif not quiet:
                    print(f"Найден Python, но версия не совпадает: {version_output}")
            except Exception as e:
                if not quiet:
                    print(f"Не удалось проверить версию найденного Python: {e}")
        
        # Метод 3: Пытаемся использовать pyenv (только уже установленные в offline)
        if use_pyenv and not offline:
            if self._pyenv_manager is None:
                try:
                    from .pyenv_manager import PyenvManager
                    self._pyenv_manager = PyenvManager()
                except ImportError:
                    self._pyenv_manager = None
            
            if self._pyenv_manager and self._pyenv_manager.pyenv_available:
                if not quiet:
                    print(f"Попытка установки Python {version} через pyenv...")
                # Нормализуем версию для pyenv (нужна полная версия)
                pyenv_version = self._normalize_version_for_pyenv(version)
                if pyenv_version:
                    if self._pyenv_manager.version_installed(pyenv_version):
                        python_path = self._pyenv_manager.get_python_path(pyenv_version)
                        if python_path:
                            if not quiet:
                                print(f"Используется Python {version} из pyenv: {python_path}")
                            return python_path
                    else:
                        # Пытаемся установить через pyenv
                        if self._pyenv_manager.install_version(pyenv_version):
                            python_path = self._pyenv_manager.get_python_path(pyenv_version)
                            if python_path:
                                if not quiet:
                                    print(f"Python {version} установлен через pyenv: {python_path}")
                                return python_path
        
        # Метод 3b: pyenv уже установленные версии (offline)
        if use_pyenv and offline:
            if self._pyenv_manager is None:
                try:
                    from .pyenv_manager import PyenvManager
                    self._pyenv_manager = PyenvManager()
                except ImportError:
                    self._pyenv_manager = None
            if self._pyenv_manager and self._pyenv_manager.pyenv_available:
                pyenv_version = self._normalize_version_for_pyenv(version)
                if pyenv_version and self._pyenv_manager.version_installed(pyenv_version):
                    python_path = self._pyenv_manager.get_python_path(pyenv_version)
                    if python_path:
                        if not quiet:
                            print(f"Используется Python {version} из pyenv: {python_path}")
                        return python_path
        
        # Метод 4: Скачиваем и устанавливаем автоматически (не в offline)
        if not offline and self.download_and_install_python(version, quiet=quiet):
            python_path = self.get_python_path(version)
            if python_path and python_path.exists():
                return python_path
        
        # Если не удалось найти или установить нужную версию
        if offline:
            raise RuntimeError(
                f"Python {version} не найден. Режим --offline: используйте только уже установленные версии."
            )
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
