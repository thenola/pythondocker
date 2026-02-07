"""Модуль для запуска скриптов в Docker-контейнерах."""

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict


# Маппинг версий Python на Docker-образы (официальные на Docker Hub)
# Теперь поддерживаются любые версии Python, доступные на Docker Hub
DOCKER_IMAGES = {
    '2.7': 'python:2.7-slim',
    '3.6': 'python:3.6-slim',
    '3.7': 'python:3.7-slim',
    '3.8': 'python:3.8-slim',
    '3.9': 'python:3.9-slim',
    '3.10': 'python:3.10-slim',
    '3.11': 'python:3.11-slim',
    '3.12': 'python:3.12-slim',
    '3.13': 'python:3.13-slim',
    '3.14': 'python:3.14-slim',
    'pypy2.7': 'pypy:2.7-slim',
    'pypy3.9': 'pypy:3.9-slim',
    'pypy3.10': 'pypy:3.10-slim',
    'pypy3.11': 'pypy:3.11-slim',
}


def docker_available() -> bool:
    """Проверяет, доступен ли Docker и демон запущен."""
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def get_docker_image(python_version: str) -> str:
    """
    Возвращает Docker-образ для указанной версии Python.
    
    Теперь поддерживает любую версию Python, автоматически формируя имя образа.
    Если образ не существует на Docker Hub, Docker выдаст ошибку при запуске.
    
    Args:
        python_version: Версия Python (2.7, 3.11, 3.14, pypy3.11 и т.д.)
        
    Returns:
        Имя образа (например python:3.11-slim или python:3.14-slim)
    """
    # Нормализация: убираем лишние части версии
    v = python_version.lower().strip()
    
    # Прямое совпадение с известными образами
    if v in DOCKER_IMAGES:
        return DOCKER_IMAGES[v]
    
    # PyPy: pypy3.11.1 -> pypy3.11
    if v.startswith('pypy'):
        # Проверяем известные образы
        for key in DOCKER_IMAGES:
            if key.startswith('pypy') and key in v:
                return DOCKER_IMAGES[key]
        # Пытаемся извлечь версию: pypy3.11 -> pypy3.11
        parts = v.replace('pypy', '').split('.')
        if len(parts) >= 2:
            short = f"pypy{parts[0]}.{parts[1]}"
            # Проверяем в известных образах
            if short in DOCKER_IMAGES:
                return DOCKER_IMAGES[short]
            # Формируем имя образа для любой версии PyPy
            return f"pypy:{parts[0]}.{parts[1]}-slim"
        # Если не удалось распарсить, возвращаем как есть
        return f"pypy:{v.replace('pypy', '')}-slim"
    
    # CPython: 3.11.5 -> 3.11, 3.14 -> 3.14
    parts = v.split('.')
    if len(parts) >= 2:
        short = f"{parts[0]}.{parts[1]}"
        # Проверяем в известных образах
        if short in DOCKER_IMAGES:
            return DOCKER_IMAGES[short]
        # Формируем имя образа для любой версии Python
        return f"python:{short}-slim"
    
    # Если передана только мажорная версия (например, "3")
    if len(parts) == 1:
        # Для Python 2 используем 2.7
        if parts[0] == '2':
            return 'python:2.7-slim'
        # Для Python 3 используем последнюю известную версию
        return 'python:3.13-slim'
    
    # Если ничего не подошло, пробуем использовать как есть
    return DOCKER_IMAGES.get(v, f"python:{v}-slim")


def _path_for_docker(path: Path) -> str:
    r"""
    Преобразует путь в формат для docker run -v.
    Windows: Docker Desktop принимает C:\path или C:/path
    Unix: /path
    """
    path = path.resolve()
    s = str(path)
    if os.name == 'nt' and len(s) >= 2 and s[1] == ':':
        # Docker Desktop Windows: C:\path или C:/path
        return s.replace('\\', '/')
    return s.replace('\\', '/')


def run_in_docker(
    script_path: str,
    python_version: str,
    args: Optional[List[str]] = None,
    env_vars: Optional[Dict[str, str]] = None,
    requirements_path: Optional[str] = None,
    encoding: Optional[str] = None,
    work_dir: Optional[str] = None,
    script_display_name: Optional[str] = None,
    log_file: Optional[str] = None,
    quiet: bool = False,
    no_deps: bool = False,
) -> int:
    """
    Запускает Python-скрипт в Docker-контейнере.
    
    Args:
        script_path: Путь к скрипту
        python_version: Версия Python (2.7, 3.11, pypy3.11 и т.д.)
        args: Аргументы для скрипта
        env_vars: Переменные окружения
        requirements_path: Путь к requirements.txt
        encoding: Кодировка
        work_dir: Рабочая директория
        script_display_name: Имя для отображения
        log_file: Файл для логирования
        quiet: Скрыть служебные сообщения
        no_deps: Не устанавливать зависимости
        
    Returns:
        Код возврата процесса
    """
    if not docker_available():
        raise RuntimeError(
            "Docker недоступен. Убедитесь, что Docker установлен и демон запущен "
            "(docker info). Используйте режим без --docker (venv)."
        )
    
    image = get_docker_image(python_version)
    if not image:
        raise RuntimeError(
            f"Не удалось определить Docker-образ для Python {python_version}. "
            "Проверьте правильность указания версии."
        )
    
    script_path = Path(script_path).resolve()
    if not script_path.exists():
        raise FileNotFoundError(f"Скрипт не найден: {script_path}")
    
    # Jython не поддерживается в Docker-режиме
    if 'jython' in python_version.lower():
        raise RuntimeError(
            "Jython не поддерживается в Docker-режиме. Используйте venv (без --docker)."
        )
    
    cwd = Path(work_dir) if work_dir else script_path.parent
    cwd = cwd.resolve()
    
    # База для монтирования: общий предок cwd и requirements (если requirements вне cwd)
    mount_base = cwd
    if requirements_path and not no_deps:
        req_path = Path(requirements_path)
        if not req_path.is_absolute():
            req_path = (cwd / req_path).resolve()
        if req_path.exists() and req_path.is_file():
            try:
                req_path.relative_to(cwd)
            except ValueError:
                # requirements вне cwd — монтируем общий предок
                try:
                    mount_base = Path(os.path.commonpath([str(cwd), str(req_path.parent)]))
                except (ValueError, TypeError):
                    pass
    
    # Монтируем mount_base в /work
    host_path = _path_for_docker(mount_base)
    container_work = "/work"
    
    try:
        script_rel = script_path.relative_to(mount_base)
    except ValueError:
        script_rel = Path(script_path.name)
    script_in_container = str(Path(container_work) / script_rel).replace('\\', '/')
    
    # Рабочая директория в контейнере = родитель скрипта
    try:
        script_parent_rel = script_path.parent.relative_to(mount_base)
        container_cwd = str(Path(container_work) / script_parent_rel).replace('\\', '/')
    except ValueError:
        container_cwd = container_work
    
    # Собираем команду docker run
    cmd = [
        'docker', 'run', '--rm',
        '-v', f'{host_path}:{container_work}',
        '-w', container_cwd,
        '-e', 'PYTHONUNBUFFERED=1',
    ]
    
    if encoding:
        cmd.extend(['-e', f'PYTHONIOENCODING={encoding}:replace'])
    
    if env_vars:
        for k, v in env_vars.items():
            cmd.extend(['-e', f'{k}={v}'])
    
    # Интерактивный режим для stdin (без -t чтобы не ломать CI/pipe)
    cmd.extend(['-i'])
    
    cmd.append(image)
    
    # Устанавливаем зависимости перед запуском (если нужно)
    if requirements_path and not no_deps:
        req_path = Path(requirements_path)
        if not req_path.is_absolute():
            req_path = (cwd / req_path).resolve()
        if req_path.exists():
            try:
                rel_req = req_path.relative_to(mount_base)
                req_arg = str(rel_req).replace('\\', '/')
            except ValueError:
                req_arg = req_path.name
            if not quiet:
                print(f"Установка зависимостей из requirements.txt в контейнере...")
            req_dir = Path(req_arg).parent
            pip_work = str(Path(container_work) / req_dir).replace('\\', '/') if req_dir.parts else container_work
            pip_req_arg = Path(req_arg).name if req_dir.parts else req_arg
            pip_cmd = ['docker', 'run', '--rm',
                       '-v', f'{host_path}:{container_work}',
                       '-w', pip_work,
                       image,
                       'pip', 'install', '-r', pip_req_arg]
            pip_result = subprocess.run(pip_cmd, capture_output=True, text=False)
            if pip_result.returncode != 0 and not quiet:
                err = (pip_result.stderr or b'').decode(errors='replace').strip()
                print(f"Предупреждение: не удалось установить зависимости: {err or 'см. вывод выше'}")
    
    # Команда запуска скрипта
    cmd.extend(['python', script_in_container])
    if args:
        cmd.extend(args)
    
    display_name = script_display_name or script_path.name
    if not quiet:
        print(f"Запуск {display_name} в Docker ({image})...")
        print(f"  Образ: {image}")
        print(f"  Рабочая директория: {script_path.parent}")
    
    if log_file:
        log_path = Path(log_file)
        if not log_path.is_absolute():
            log_path = Path(cwd) / log_path
        with open(log_path, 'w', encoding='utf-8', errors='replace') as f:
            result = subprocess.run(cmd, cwd=str(mount_base), stdout=f, stderr=subprocess.STDOUT)
        if not quiet:
            print(f"Вывод сохранён в {log_path}")
        return result.returncode
    
    result = subprocess.run(cmd, cwd=str(mount_base))
    return result.returncode


def run_shell_in_docker(python_version: str, cwd: Optional[str] = None, quiet: bool = False) -> int:
    """
    Запускает интерактивную оболочку Python в Docker-контейнере.
    
    Args:
        python_version: Версия Python
        cwd: Рабочая директория
        quiet: Скрыть сообщения
        
    Returns:
        Код возврата
    """
    if not docker_available():
        raise RuntimeError("Docker недоступен. Убедитесь, что Docker установлен и запущен.")
    
    image = get_docker_image(python_version)
    if not image:
        raise RuntimeError(
            f"Не удалось определить Docker-образ для Python {python_version}. "
            "Проверьте правильность указания версии."
        )
    
    work_dir = Path(cwd).resolve() if cwd else Path.cwd()
    host_path = _path_for_docker(work_dir)
    
    cmd = [
        'docker', 'run', '--rm', '-it',
        '-v', f'{host_path}:/work',
        '-w', '/work',
        image,
        'python', '-i',
    ]
    
    if not quiet:
        print(f"Запуск Python shell в Docker ({image})...")
        print("(Введите exit() для выхода)\n")
    
    return subprocess.call(cmd, cwd=str(work_dir))
