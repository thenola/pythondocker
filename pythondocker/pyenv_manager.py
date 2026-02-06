"""Модуль для работы с pyenv."""

import os
import subprocess
import platform
from pathlib import Path
from typing import Optional


class PyenvManager:
    """Управляет версиями Python через pyenv."""
    
    def __init__(self):
        self.pyenv_available = self._check_pyenv_available()
        self.pyenv_root = self._get_pyenv_root()
    
    def _check_pyenv_available(self) -> bool:
        """Проверяет доступность pyenv."""
        try:
            result = subprocess.run(
                ['pyenv', '--version'],
                capture_output=True,
                text=True,
                timeout=3
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _get_pyenv_root(self) -> Optional[Path]:
        """Получает корневую директорию pyenv."""
        if not self.pyenv_available:
            return None
        
        try:
            # Проверяем переменную окружения PYENV_ROOT
            pyenv_root = os.environ.get('PYENV_ROOT')
            if pyenv_root:
                return Path(pyenv_root)
            
            # Стандартные пути
            home = Path.home()
            system = platform.system().lower()
            
            if system == 'windows':
                # Windows: обычно в %USERPROFILE%\.pyenv
                return home / '.pyenv'
            else:
                # Unix: обычно в ~/.pyenv
                return home / '.pyenv'
        except Exception:
            return None
    
    def version_installed(self, version: str) -> bool:
        """
        Проверяет, установлена ли версия Python через pyenv.
        
        Args:
            version: Версия Python (например, '2.7.18', '3.11.0')
            
        Returns:
            True если версия установлена
        """
        if not self.pyenv_available:
            return False
        
        try:
            result = subprocess.run(
                ['pyenv', 'versions', '--bare'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                installed_versions = result.stdout.strip().split('\n')
                # Проверяем точное совпадение или начало версии
                for installed in installed_versions:
                    if installed.strip() == version or installed.strip().startswith(version):
                        return True
            return False
        except Exception:
            return False
    
    def install_version(self, version: str) -> bool:
        """
        Устанавливает версию Python через pyenv.
        
        Args:
            version: Версия Python для установки
            
        Returns:
            True если установка успешна
        """
        if not self.pyenv_available:
            print("pyenv не доступен. Установите pyenv: https://github.com/pyenv/pyenv")
            return False
        
        if self.version_installed(version):
            print(f"Python {version} уже установлен через pyenv")
            return True
        
        print(f"Установка Python {version} через pyenv...")
        print("Это может занять некоторое время...")
        
        try:
            # Устанавливаем через pyenv install
            result = subprocess.run(
                ['pyenv', 'install', version],
                capture_output=False,  # Показываем вывод в реальном времени
                text=True,
                timeout=None  # Установка может занять много времени
            )
            
            if result.returncode == 0:
                print(f"Python {version} успешно установлен через pyenv")
                return True
            else:
                print(f"Ошибка при установке Python {version} через pyenv")
                return False
                
        except subprocess.TimeoutExpired:
            print("Установка прервана по таймауту")
            return False
        except Exception as e:
            print(f"Ошибка при установке через pyenv: {e}")
            return False
    
    def get_python_path(self, version: str) -> Optional[Path]:
        """
        Получает путь к Python определенной версии через pyenv.
        
        Args:
            version: Версия Python
            
        Returns:
            Path к исполняемому файлу Python или None
        """
        if not self.pyenv_available or not self.pyenv_root:
            return None
        
        if not self.version_installed(version):
            return None
        
        # Путь к Python в pyenv
        system = platform.system().lower()
        if system == 'windows':
            python_exe = self.pyenv_root / 'versions' / version / 'python.exe'
        else:
            python_exe = self.pyenv_root / 'versions' / version / 'bin' / 'python'
        
        if python_exe.exists():
            return python_exe
        
        # Пробуем найти через pyenv which
        try:
            result = subprocess.run(
                ['pyenv', 'which', 'python'],
                env={**os.environ, 'PYENV_VERSION': version},
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass
        
        return None
