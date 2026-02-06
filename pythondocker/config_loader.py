"""Загрузка конфигурации из .pythondocker.yml или .pythondocker.json."""

import json
from pathlib import Path
from typing import Optional, Dict, Any, Tuple


CONFIG_NAMES = ['.pythondocker.yml', '.pythondocker.yaml', '.pythondocker.json']


def _load_yaml(path: Path) -> Optional[Dict[str, Any]]:
    """Загружает YAML файл (если PyYAML установлен)."""
    try:
        import yaml
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return yaml.safe_load(f)
    except ImportError:
        return None
    except Exception:
        return None


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Загружает JSON файл."""
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return json.load(f)
    except Exception:
        return None


def find_config(start_dir: Path) -> Optional[Path]:
    """
    Ищет конфигурационный файл, начиная с start_dir и поднимаясь вверх.
    Приоритет: .pythondocker.json (без зависимостей), затем .pythondocker.yml
    
    Args:
        start_dir: Директория для начала поиска (обычно директория скрипта)
        
    Returns:
        Path к конфигу или None
    """
    current = Path(start_dir).resolve()
    
    def search_in_dir(d: Path) -> Optional[Path]:
        for name in ['.pythondocker.json', '.pythondocker.yml', '.pythondocker.yaml']:
            p = d / name
            if p.exists() and p.is_file():
                return p
        return None
    
    for _ in range(32):  # Макс. 32 уровня вверх
        found = search_in_dir(current)
        if found:
            return found
        parent = current.parent
        if parent == current:
            break
        current = parent
    
    return None


def load_config(script_path: str) -> Tuple[Optional[Dict[str, Any]], Optional[Path]]:
    """
    Загружает конфигурацию для скрипта.
    
    Ищет .pythondocker.yml или .pythondocker.json в директории скрипта
    и родительских директориях.
    
    Args:
        script_path: Путь к запускаемому скрипту
        
    Returns:
        Tuple (config_dict, config_base_dir) or (None, None)
    """
    start_dir = Path(script_path).parent.resolve()
    config_path = find_config(start_dir)
    
    if not config_path:
        return None, None
    
    if config_path.suffix.lower() in ('.yml', '.yaml'):
        config = _load_yaml(config_path)
        if config is None:
            config = _load_json(config_path)
    else:
        config = _load_json(config_path)
    
    if not config or not isinstance(config, dict):
        return None, None
    
    return config, config_path.parent


def apply_config(config: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
    """
    Применяет конфигурацию: нормализует пути, обрабатывает env.
    
    Args:
        config: Сырая конфигурация
        base_dir: Базовая директория (где найден конфиг) для относительных путей
        
    Returns:
        Обработанная конфигурация
    """
    result = {}
    
    if 'python' in config:
        result['python_version'] = str(config['python'])
    elif 'default_interpreter' in config:
        result['python_version'] = str(config['default_interpreter'])
    
    if 'requirements' in config:
        req = config['requirements']
        if isinstance(req, str):
            req_path = Path(req)
            if not req_path.is_absolute():
                req_path = base_dir / req_path
            if req_path.exists():
                result['requirements'] = str(req_path)
            else:
                result['requirements'] = req
        else:
            result['requirements'] = str(req)
    
    if 'encoding' in config:
        result['encoding'] = str(config['encoding'])
    
    if 'env' in config:
        env = config['env']
        if isinstance(env, dict):
            result['env'] = {str(k): str(v) for k, v in env.items()}
        elif isinstance(env, list):
            result['env'] = {}
            for item in env:
                if isinstance(item, str) and '=' in item:
                    key, val = item.split('=', 1)
                    result['env'][key.strip()] = val.strip()
        else:
            result['env'] = {}
    
    if 'args' in config:
        args = config['args']
        if isinstance(args, list):
            result['args'] = [str(a) for a in args]
        else:
            result['args'] = []
    
    if 'docker' in config:
        val = config['docker']
        result['docker'] = bool(val) if isinstance(val, bool) else str(val).lower() in ('1', 'true', 'yes', 'on')

    # PyPy: PYPY_JIT_OPTIONS. Jython: JAVA_OPTS
    if 'pypy_jit_options' in config:
        result['pypy_jit_options'] = str(config['pypy_jit_options'])
    if 'java_opts' in config:
        opts = config['java_opts']
        result['java_opts'] = opts if isinstance(opts, str) else ' '.join(str(o) for o in opts)
    
    return result
