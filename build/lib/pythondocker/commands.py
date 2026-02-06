"""Дополнительные команды для управления окружениями."""

import os
import shutil
from pathlib import Path
from typing import List, Dict
from .environment_manager import EnvironmentManager
from .python_installer import PythonInstaller


class Commands:
    """Дополнительные команды для управления PythonDocker."""
    
    def __init__(self):
        self.env_manager = EnvironmentManager()
        self.python_installer = PythonInstaller()
    
    def list_environments(self) -> List[Dict[str, str]]:
        """
        Список всех созданных окружений.
        
        Returns:
            Список словарей с информацией об окружениях
        """
        envs = []
        if self.env_manager.base_dir.exists():
            for env_dir in self.env_manager.base_dir.iterdir():
                if env_dir.is_dir():
                    python_exe = self.env_manager.get_python_executable(env_dir)
                    version = "unknown"
                    if python_exe.exists():
                        try:
                            import subprocess
                            result = subprocess.run(
                                [str(python_exe), '--version'],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            version_output = result.stdout.strip() or result.stderr.strip()
                            if version_output:
                                version = version_output
                        except:
                            pass
                    
                    envs.append({
                        'name': env_dir.name,
                        'path': str(env_dir),
                        'version': version,
                        'size': self._get_dir_size(env_dir)
                    })
        return envs
    
    def list_python_versions(self) -> List[Dict[str, str]]:
        """
        Список всех установленных версий Python.
        
        Returns:
            Список словарей с информацией о версиях Python
        """
        versions = []
        if self.python_installer.install_dir.exists():
            for version_dir in self.python_installer.install_dir.iterdir():
                if version_dir.is_dir():
                    python_path = self.python_installer.get_python_path(version_dir.name)
                    if python_path and python_path.exists():
                        versions.append({
                            'version': version_dir.name,
                            'path': str(python_path),
                            'size': self._get_dir_size(version_dir)
                        })
        return versions
    
    def clean_environments(self, dry_run: bool = False) -> int:
        """
        Удаляет неиспользуемые окружения.
        
        Args:
            dry_run: Если True, только показывает что будет удалено
            
        Returns:
            Количество удаленных окружений
        """
        # Пока просто удаляем все окружения старше 30 дней
        # В будущем можно добавить более умную логику
        import time
        removed = 0
        if self.env_manager.base_dir.exists():
            for env_dir in self.env_manager.base_dir.iterdir():
                if env_dir.is_dir():
                    # Проверяем время последнего доступа
                    try:
                        mtime = env_dir.stat().st_mtime
                        age_days = (time.time() - mtime) / (24 * 3600)
                        if age_days > 30:
                            if dry_run:
                                print(f"Будет удалено: {env_dir.name} (не использовалось {age_days:.0f} дней)")
                            else:
                                shutil.rmtree(env_dir)
                                print(f"Удалено: {env_dir.name}")
                                removed += 1
                    except Exception as e:
                        print(f"Ошибка при проверке {env_dir.name}: {e}")
        return removed
    
    def remove_python_version(self, version: str, dry_run: bool = False) -> bool:
        """
        Удаляет установленную версию Python.
        
        Args:
            version: Версия Python для удаления
            dry_run: Если True, только показывает что будет удалено
            
        Returns:
            True если удаление успешно
        """
        version_dir = self.python_installer.install_dir / version
        if version_dir.exists():
            if dry_run:
                print(f"Будет удалена версия Python: {version}")
                print(f"Путь: {version_dir}")
                return True
            else:
                try:
                    shutil.rmtree(version_dir)
                    print(f"Версия Python {version} удалена")
                    return True
                except Exception as e:
                    print(f"Ошибка при удалении: {e}")
                    return False
        else:
            print(f"Версия Python {version} не найдена")
            return False
    
    def info(self) -> Dict:
        """
        Выводит информацию о системе PythonDocker.
        
        Returns:
            Словарь с информацией
        """
        info = {
            'python_versions': len(self.list_python_versions()),
            'environments': len(self.list_environments()),
            'python_dir': str(self.python_installer.install_dir),
            'envs_dir': str(self.env_manager.base_dir),
            'pyenv_available': False
        }
        
        # Проверяем pyenv
        try:
            from .pyenv_manager import PyenvManager
            pyenv_mgr = PyenvManager()
            info['pyenv_available'] = pyenv_mgr.pyenv_available
        except:
            pass
        
        return info
    
    def _get_dir_size(self, path: Path) -> int:
        """Вычисляет размер директории в байтах."""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except:
            pass
        return total
    
    def format_size(self, size_bytes: int) -> str:
        """Форматирует размер в читаемый формат."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
