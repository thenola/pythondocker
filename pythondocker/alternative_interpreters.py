"""Поддержка альтернативных интерпретаторов: PyPy, Jython."""

import os
import platform
import subprocess
import sys
import urllib.request
import urllib.error
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import Optional, Tuple

# Соответствие версий PyPy и релизов (PyPy v7.3.20 - июль 2025)
PYPY_RELEASES = {
    'pypy3.11': ('7.3.20', 'pypy3.11-v7.3.20'),
    'pypy3.10': ('7.3.19', 'pypy3.10-v7.3.19'),
    'pypy2.7': ('7.3.20', 'pypy2.7-v7.3.20'),
    'pypy3.9': ('7.3.16', 'pypy3.9-v7.3.16'),
}

JYTHON_URL = "https://repo1.maven.org/maven2/org/python/jython-standalone/2.7.4/jython-standalone-2.7.4.jar"


def _get_cache_dir() -> Path:
    """Директория кэша для архивов PyPy/Jython."""
    cache = Path.home() / '.pythondocker' / 'cache'
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def _get_cached_archive(url: str) -> Optional[Path]:
    """Возвращает путь к архиву в кэше, если он есть."""
    name = url.split('/')[-1]
    cached = _get_cache_dir() / name
    return cached if cached.exists() else None


def _save_to_cache(url: str, src_path: Path) -> Path:
    """Сохраняет архив в кэш."""
    name = url.split('/')[-1]
    cache_dir = _get_cache_dir()
    dest = cache_dir / name
    if not dest.exists() or dest.stat().st_size != src_path.stat().st_size:
        shutil.copy2(src_path, dest)
    return dest


def java_available() -> bool:
    """
    Проверяет, установлена ли Java в системе (нужна для Jython).
    
    Returns:
        True если команда java доступна
    """
    try:
        subprocess.run(
            ['java', '-version'],
            capture_output=True,
            timeout=5
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def is_alternative_interpreter(version: str) -> Optional[str]:
    """
    Определяет, является ли версия альтернативным интерпретатором.
    
    Returns:
        'pypy', 'jython' или None
    """
    v = version.lower().strip()
    if v.startswith('pypy'):
        return 'pypy'
    if v.startswith('jython'):
        return 'jython'
    return None


def get_pypy_url(version: str) -> Optional[str]:
    """Формирует URL для скачивания PyPy."""
    # Нормализуем: pypy3.11, pypy2.7
    v = version.lower().replace(' ', '')
    if not v.startswith('pypy'):
        v = 'pypy' + v
    
    if v not in PYPY_RELEASES:
        # Пробуем pypy3.11, pypy2.7
        for key in PYPY_RELEASES:
            if key.startswith(v) or v.startswith(key):
                v = key
                break
        else:
            return None
    
    pypy_ver, pypy_name = PYPY_RELEASES.get(v, (None, None))
    if not pypy_ver:
        return None
    
    system, arch = _get_platform_suffix()
    if not system:
        return None
    
    base = "https://downloads.python.org/pypy"
    
    if system == 'windows':
        return f"{base}/{pypy_name}-win64.zip"
    elif system == 'linux':
        if arch == 'aarch64':
            return f"{base}/{pypy_name}-aarch64.tar.bz2"
        return f"{base}/{pypy_name}-linux64.tar.bz2"
    elif system == 'macos':
        if arch == 'arm64':
            return f"{base}/{pypy_name}-macos_arm64.tar.bz2"
        return f"{base}/{pypy_name}-macos_x86_64.tar.bz2"
    return None


def _get_platform_suffix() -> Tuple[Optional[str], str]:
    """Возвращает (system, arch) для выбора бинарника."""
    sys_name = platform.system().lower()
    machine = platform.machine().lower()
    
    if sys_name == 'windows':
        return 'windows', 'amd64' if '64' in machine or machine in ('x86_64', 'amd64') else 'win32'
    elif sys_name == 'darwin':
        arch = 'arm64' if 'arm' in machine else 'x86_64'
        return 'macos', arch
    elif sys_name == 'linux':
        arch = 'aarch64' if machine in ('aarch64', 'arm64') else 'x86_64'
        return 'linux', arch
    return None, machine


def _download_with_progress(url: str, dest_path: Path, quiet: bool = False) -> bool:
    """
    Скачивает файл с отображением прогресса.
    
    Args:
        url: URL для скачивания
        dest_path: Путь для сохранения
        quiet: Скрыть прогресс
        
    Returns:
        True если успешно
    """
    def _reporthook(block_num, block_size, total_size):
        if quiet or total_size <= 0:
            return
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 // total_size)
            mb_done = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            line = f"\rСкачивание: {percent}% ({mb_done:.1f} / {mb_total:.1f} MB)"
            sys.stdout.write(line)
            sys.stdout.flush()
            if percent >= 100:
                sys.stdout.write("\n")
    
    try:
        urllib.request.urlretrieve(url, dest_path, reporthook=_reporthook if not quiet else None)
        return True
    except Exception:
        return False


def install_pypy(version: str, install_dir: Path, quiet: bool = False) -> Optional[Path]:
    """
    Скачивает и устанавливает PyPy.
    
    Returns:
        Path к python/pypy3 исполняемому файлу или None
    """
    url = get_pypy_url(version)
    if not url:
        return None
    
    v_norm = version.lower().replace(' ', '')
    if not v_norm.startswith('pypy'):
        v_norm = 'pypy' + v_norm
    
    version_dir = install_dir / v_norm
    version_dir.mkdir(parents=True, exist_ok=True)
    
    if not quiet:
        print(f"Скачивание PyPy {version} из {url}...")
    
    try:
        archive_path = version_dir / "pypy_archive" + (".zip" if url.endswith('.zip') else ".tar.bz2")
        cached = _get_cached_archive(url)
        if cached:
            if not quiet:
                print(f"Используется кэш: {cached.name}")
            shutil.copy2(cached, archive_path)
        elif not _download_with_progress(url, archive_path, quiet=quiet):
            return None
        else:
            _save_to_cache(url, archive_path)
        
        if not quiet:
            print("Распаковка PyPy...")
        
        extract_dir = version_dir / "extract"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir()
        
        if url.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(extract_dir)
        else:
            with tarfile.open(archive_path, 'r:bz2') as tf:
                tf.extractall(extract_dir)
        
        archive_path.unlink(missing_ok=True)
        
        # PyPy распаковывается в pypy3.11-v7.3.20-win64/ или аналогично
        pypy_dir = None
        for item in extract_dir.iterdir():
            if item.is_dir() and 'pypy' in item.name.lower():
                pypy_dir = item
                break
        
        if not pypy_dir:
            return None
        
        # Ищем python/pypy3 исполняемый файл
        python_exe = None
        if os.name == 'nt':
            for name in ('pypy3.exe', 'python.exe', 'pypy.exe'):
                exe = pypy_dir / name
                if exe.exists():
                    python_exe = exe
                    break
            if not python_exe:
                for f in pypy_dir.rglob('pypy3.exe'):
                    python_exe = f
                    break
        else:
            for path in (pypy_dir / 'bin' / 'pypy3', pypy_dir / 'bin' / 'python', pypy_dir / 'bin' / 'pypy'):
                if path.exists():
                    python_exe = path
                    break
        
        if not python_exe or not python_exe.exists():
            return None
        
        rel_path = python_exe.relative_to(pypy_dir)
        
        # Перемещаем в version_dir
        target_dir = version_dir / 'pypy'
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.move(str(pypy_dir), str(target_dir))
        shutil.rmtree(extract_dir, ignore_errors=True)
        
        result_exe = target_dir / rel_path
        if not result_exe.exists():
            result_exe = target_dir / ('bin/pypy3' if os.name != 'nt' else 'pypy3.exe')
        
        if result_exe.exists():
            if not quiet:
                print(f"PyPy {version} установлен: {result_exe}")
            return result_exe
        return None
        
    except Exception as e:
        if not quiet:
            print(f"Ошибка при установке PyPy: {e}")
        return None


def install_jython(install_dir: Path, quiet: bool = False) -> Optional[Path]:
    """
    Скачивает Jython standalone JAR.
    Требует Java в системе.
    
    Returns:
        Path к jython-standalone-2.7.4.jar или None
    """
    if not java_available():
        if not quiet:
            print("Ошибка: Jython требует Java. Установите Java (java -version) и повторите.")
        return None
    
    jython_dir = install_dir / 'jython2.7'
    jython_dir.mkdir(parents=True, exist_ok=True)
    jar_path = jython_dir / 'jython-standalone-2.7.4.jar'
    
    if jar_path.exists():
        if not quiet:
            print(f"Jython уже установлен: {jar_path}")
        return jar_path
    
    if not quiet:
        print("Скачивание Jython...")
    
    try:
        cached = _get_cached_archive(JYTHON_URL)
        if cached:
            if not quiet:
                print(f"Используется кэш: {cached.name}")
            shutil.copy2(cached, jar_path)
        else:
            if not _download_with_progress(JYTHON_URL, jar_path, quiet=quiet):
                if jar_path.exists():
                    jar_path.unlink(missing_ok=True)
                return None
            _save_to_cache(JYTHON_URL, jar_path)
        if not quiet:
            print(f"Jython установлен: {jar_path}")
        return jar_path
    except Exception as e:
        if not quiet:
            print(f"Ошибка при установке Jython: {e}")
        return None


def run_jython_script(jar_path: Path, script_path: str, args: Optional[list] = None) -> int:
    """Запускает скрипт через Jython (java -jar jython.jar script.py)."""
    import subprocess
    cmd = ['java', '-jar', str(jar_path), str(script_path)]
    if args:
        cmd.extend(args)
    return subprocess.call(cmd)
