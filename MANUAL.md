# PythonDocker — подробная справка

Версия: см. `pythondocker -v`  
Репозиторий: https://github.com/thenola/pythondocker

---

## 1. Назначение программы

**PythonDocker** — утилита командной строки для запуска Python-скриптов (.py) и Jupyter Notebook (.ipynb) в изолированных окружениях с автоматическим выбором версии интерпретатора.

**Режимы работы:**
- **venv** (по умолчанию) — виртуальные окружения Python
- **Docker** (флаг `--docker`) — выполнение в Docker-контейнерах

Программа решает задачи:
- Запуск legacy-скриптов под Python 2.7 без установки его в систему
- Запуск скриптов под разными версиями Python (3.8, 3.11 и т.д.) в изоляции
- Автоматическая установка зависимостей из requirements.txt
- Использование PyPy и Jython без их отдельной настройки

---

## 2. Синтаксис вызова

```
pythondocker [OPTIONS] [SCRIPT] [--args ARG1 ARG2 ...]
pythondocker <COMMAND> [OPTIONS]
```

**Режим скрипта:** `SCRIPT` — путь к .py или .ipynb. При отсутствии скрипта обязателен `--shell`.

**Режим команды:** первый аргумент — одна из команд: `list`, `info`, `clean`, `remove`, `freeze`, `completions`, `help`.

---

## 3. Команды

### 3.1. `list`

Список созданных виртуальных окружений (venv). Docker-режим не создаёт окружений в ~/.pythondocker/envs.

```
pythondocker list
```

**Вывод:** имя окружения, версия Python, размер на диске.

---

### 3.2. `info`

Сводная информация о PythonDocker.

```
pythondocker info
```

**Показывает:**
- Количество установленных версий Python
- Количество окружений
- Путь к каталогу Python: `~/.pythondocker/python/`
- Путь к каталогу окружений: `~/.pythondocker/envs/`
- Доступность pyenv
- Доступность Docker
- Список установленных версий Python и их размер

---

### 3.3. `clean [--dry-run]`

Удаление окружений, не использовавшихся более 30 дней.

```
pythondocker clean
pythondocker clean --dry-run
```

`--dry-run` — только показать, что будет удалено, без удаления.

---

### 3.4. `remove <VERSION> [--dry-run]`

Удаление установленной версии Python.

```
pythondocker remove 2.7
pythondocker remove 3.11
pythondocker remove pypy3.11
pythondocker remove jython
pythondocker remove 2.7 --dry-run
```

`<VERSION>` — версия (2.7, 3.11, pypy3.11, jython и т.д.).

---

### 3.5. `freeze [OPTIONS]`

Экспорт зависимостей (pip freeze) в файл или stdout.

```
pythondocker freeze
pythondocker freeze -o requirements.txt
pythondocker freeze --current -o requirements.txt
pythondocker freeze --python 3.11 -o req.txt
pythondocker freeze script.py -o req.txt
```

**Опции:**
| Опция | Описание |
|-------|----------|
| `-o FILE`, `--output FILE` | Файл для сохранения (по умолчанию — stdout) |
| `-p VER`, `--python VER` | Версия Python окружения |
| `-c`, `--current` | Использовать текущий Python (окружение, в котором запущен pythondocker) |
| `SCRIPT` | Скрипт для автоопределения версии Python |

---

### 3.6. `completions SHELL`

Генерация скрипта автодополнения для shell.

```
pythondocker completions bash
pythondocker completions zsh
pythondocker completions powershell
```

**Использование:**
```bash
# bash/zsh
source <(pythondocker completions bash)

# PowerShell
pythondocker completions powershell | Out-String | Invoke-Expression
```

---

### 3.7. `help`

Вывод подробной справки (этого руководства).

```
pythondocker help
```

---

## 4. Параметры запуска скрипта

### 4.1. Интерпретатор и режим

| Параметр | Краткая | Описание |
|----------|---------|----------|
| `--python VER` | `-p` | Версия Python: 2.7, 3.8–3.13, pypy3.11, jython |
| `--shell` | — | Запустить интерактивный Python shell вместо скрипта |
| `--docker` | — | Запуск в Docker-контейнере вместо venv |

### 4.2. Зависимости

| Параметр | Краткая | Описание |
|----------|---------|----------|
| `--requirements FILE` | `-r` | Путь к requirements.txt |
| `--no-deps` | — | Не устанавливать зависимости |

### 4.3. Аргументы и окружение

| Параметр | Описание |
|----------|----------|
| `--args ARG1 ARG2 ...` | Аргументы, передаваемые скрипту после `--args` |
| `--env KEY=VALUE ...` | Переменные окружения (можно несколько) |

### 4.4. Кодировка и вывод

| Параметр | Краткая | Описание |
|----------|---------|----------|
| `--encoding CODEC` | `-e` | Кодировка: utf-8, cp1251, cp866, latin1 и др. |
| `--log-file FILE` | `-l` | Запись stdout и stderr в файл |
| `--verbose` | — | Подробный вывод |
| `--debug` | `-d` | Служебные сообщения (создание окружения, версия Python и т.п.) |

### 4.5. Окружение и поведение

| Параметр | Описание |
|----------|----------|
| `--force-recreate` | Пересоздать окружение, если оно уже существует |
| `--offline` | Не скачивать новые версии Python; использовать только установленные |
| `--version` | `-v` | Показать версию и URL репозитория |

---

## 5. Поддерживаемые интерпретаторы

| Тип | Версии | Примечания |
|-----|--------|------------|
| **CPython** | 2.7, 3.6–3.13 | Скачиваются с python.org |
| **PyPy** | pypy2.7, pypy3.9, pypy3.10, pypy3.11 | JIT, при загрузке — прогресс |
| **Jython** | jython | Требуется Java; Docker не поддерживается |

---

## 6. Определение версии Python

Порядок приоритета:

1. **Флаг `--python`** — явно указанная версия.
2. **Конфиг** — `python` или `default_interpreter` в .pythondocker.yml / .pythondocker.json.
3. **Shebang** — первая строка `#!/usr/bin/env python2.7` или `#!/usr/bin/python3.11`.
4. **Комментарии** — `# Requires Python 2.7`, `# Python 3.11` и т.п. в первых 20 строках.
5. **Синтаксис** — признаки Python 2: `print` без скобок, `xrange()`, `dict.iteritems()`, `raw_input()`, `unicode()`, `basestring` и др. При двух и более признаках — Python 2.7.
6. **По умолчанию** — Python 3.11 (для .ipynb и неопределённых скриптов).

---

## 7. Конфигурация

Файлы: `.pythondocker.yml`, `.pythondocker.yaml`, `.pythondocker.json`.

**Поиск:** в каталоге скрипта и родительских каталогах (до 32 уровней).

**Приоритет:** параметры CLI переопределяют значения из конфига.

### 7.1. Полный список опций конфига

| Ключ | Тип | Описание |
|------|-----|----------|
| `python` | строка | Версия Python (альтернатива: `default_interpreter`) |
| `requirements` | строка | Путь к requirements.txt |
| `encoding` | строка | Кодировка (utf-8, cp1251 и т.д.) |
| `docker` | bool/строка | `true` — использовать Docker по умолчанию |
| `env` | объект/массив | Переменные окружения KEY: VALUE или KEY=VALUE |
| `args` | массив | Аргументы по умолчанию |
| `pypy_jit_options` | строка | Опции PYPY_JIT_OPTIONS |
| `java_opts` | строка | Опции JVM для Jython (-Xmx1g и т.п.) |

### 7.2. Примеры конфигурации

**YAML (.pythondocker.yml):**
```yaml
python: "3.11"
requirements: "requirements.txt"
encoding: "cp1251"
docker: false
env:
  DEBUG: "true"
  API_KEY: "secret"
pypy_jit_options: "trace_limit=1000"
java_opts: "-Xmx1g"
```

**JSON (.pythondocker.json):**
```json
{
  "python": "3.11",
  "requirements": "requirements.txt",
  "encoding": "cp1251",
  "docker": false,
  "env": {
    "DEBUG": "true",
    "API_KEY": "secret"
  }
}
```

---

## 8. Интеграция с Docker

С флагом `--docker` скрипт выполняется в Docker-контейнере. Требуется установленный и запущенный Docker.

**Образы:** python:2.7-slim, python:3.8-slim … python:3.13-slim, pypy:2.7-slim, pypy:3.10-slim, pypy:3.11-slim.

**Поведение:**
- Рабочая директория монтируется в `/work`
- `requirements.txt` устанавливается перед запуском (если указан и нет `--no-deps`)
- Jython в Docker не поддерживается

---

## 9. Пути и каталоги

| Назначение | Путь |
|------------|------|
| Версии Python | `~/.pythondocker/python/` |
| Виртуальные окружения | `~/.pythondocker/envs/` |
| Кэш PyPy/Jython | `~/.pythondocker/cache/` |

На Windows `~` заменяется на `%USERPROFILE%`.

---

## 10. Переменные окружения (влияние на программу)

| Переменная | Описание |
|------------|----------|
| `PYENV_ROOT` | Корень pyenv (если используется) |
| `JAVA_OPTS` | Опции JVM для Jython |
| `PYPY_JIT_OPTIONS` | Опции JIT для PyPy |

---

## 11. Решение проблем

### Python не скачивается
- Проверка интернета и места на диске
- Проверка прав на `~/.pythondocker/`
- `--verbose` для детального вывода

### Docker недоступен
- Убедитесь, что Docker установлен и демон запущен: `docker info`
- Используйте режим без `--docker`

### Jython не запускается
- Установите Java: `java -version`
- Jython не поддерживается в режиме `--docker`

### Ошибки кодировки
- Укажите `--encoding cp1251` (или другую) при необходимости
- Кодировка может быть задана в `# -*- coding: ... -*-` в начале скрипта

### Зависимости не устанавливаются
- Проверьте формат requirements.txt
- `--force-recreate` для пересоздания окружения
- `--verbose` для вывода ошибок pip

---

## 12. Примеры команд

```bash
# Версия
pythondocker -v

# Простой запуск
pythondocker script.py

# Python 2.7
pythondocker script.py --python 2.7

# С зависимостями
pythondocker script.py -r requirements.txt

# Аргументы скрипту
pythondocker script.py --args file1.txt file2.txt

# Переменные окружения
pythondocker script.py --env DEBUG=1 API_KEY=xxx

# Кодировка CP1251
pythondocker script.py --encoding cp1251

# Лог в файл
pythondocker script.py -l out.log

# PyPy
pythondocker script.py --python pypy3.11

# Docker
pythondocker script.py --docker

# Интерактивный shell
pythondocker --shell --python 3.11

# Режим offline
pythondocker script.py --python 3.11 --offline
```

---

*PythonDocker — https://github.com/thenola/pythondocker*
