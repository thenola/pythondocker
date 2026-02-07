# PythonDocker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/python-docker-package.svg)](https://pypi.org/project/python-docker-package/)

**PythonDocker** — инструмент для запуска Python-скриптов (.py) и Jupyter Notebook (.ipynb) в изолированных окружениях с автоматическим определением версии интерпретатора. Поддерживает режимы **venv** (по умолчанию) и **Docker** (флаг `--docker`).

**Установка:** `pip install python-docker-package` → после установки команда: `pythondocker`

**Репозиторий:** https://github.com/thenola/pythondocker  
**PyPI:** https://pypi.org/project/python-docker-package/

## Содержание

- [Описание](#описание)
- [Возможности](#возможности)
- [Требования](#требования)
- [Интеграция с Docker](#интеграция-с-docker)
- [Установка](#установка)
- [Использование](#использование)
- [Примеры](#примеры)
- [Архитектура](#архитектура)
- [Поддерживаемые версии Python](#поддерживаемые-версии-python)
- [Управление окружениями и команды](#управление-окружениями)
- [Решение проблем](#решение-проблем)
- [Разработка](#разработка)
- [Лицензия](#лицензия)
- [Подробная справка](#подробная-справка)

## Описание

PythonDocker решает проблему запуска устаревших Python скриптов, которые требуют специфических версий Python (например, Python 2.7). Программа автоматически:

- Определяет необходимую версию Python из скрипта
- Скачивает и устанавливает нужную версию Python (если отсутствует)
- Создает изолированное виртуальное окружение
- Устанавливает зависимости из `requirements.txt`
- Запускает скрипт в изолированном окружении

**Режимы работы:** venv (виртуальные окружения) или Docker (с флагом `--docker`). Репозиторий: https://github.com/docker)

## Возможности

- **Автоматическое определение версии Python** — анализ shebang, комментариев и синтаксиса
- **Изоляция через виртуальные окружения** — каждый скрипт запускается в отдельном окружении
- **Автоматическая установка зависимостей** — поддержка `requirements.txt`
- **Автоматическое скачивание Python** — загрузка нужных версий с python.org
- **Поддержка кодировок** — автоматическое определение и управление кодировками (UTF-8, CP1251, CP866 и др.)
- **Режим venv или Docker** — по умолчанию venv; с `--docker` — запуск в Docker-контейнере
- **Кроссплатформенность** — поддержка Windows, Linux и macOS
- **Управление окружениями** — команды для просмотра, очистки и удаления окружений
- **Альтернативные интерпретаторы** — PyPy (JIT), Jython (JVM)

## Требования

- **Python 3.7+** (для запуска программы PythonDocker)
- **Доступ к интернету** (для скачивания версий Python при первом использовании)
- **Docker** — опционально (для режима `--docker`)

## Установка

### Установка через pip (рекомендуется)

```bash
# Официальный пакет на PyPI имеет другое имя:
pip install python-docker-package

# После установки команда будет доступна как:
pythondocker --version
```

**Важно:** Пакет на PyPI называется `python-docker-package`, но после установки команда будет доступна как `pythondocker`.

### Установка из исходников (для разработки)

```bash
# Клонируйте репозиторий
git clone https://github.com/thenola/pythondocker.git
cd pythondocker

# Установите пакет в режиме разработки
pip install -e .

# Или выполните обычную установку
python setup.py install
```

После установки команда `pythondocker` будет доступна в командной строке.

**Примечание**: При первом запуске программа автоматически скачает нужную версию Python, если она отсутствует локально.

## Использование

### Базовое использование

```bash
# Проверка версии и репозитория
pythondocker -v
pythondocker --version

# Автоматическое определение версии Python из скрипта
pythondocker script.py

# Указать версию Python вручную
pythondocker script.py --python 2.7

# Запуск с зависимостями из requirements.txt
pythondocker script.py --requirements requirements.txt

# Передача аргументов скрипту
pythondocker script.py --args arg1 arg2 arg3

# Установка переменных окружения
pythondocker script.py --env KEY1=value1 KEY2=value2

# Указание кодировки (полезно для Windows)
pythondocker script.py --encoding cp1251

# Подробный вывод (для отладки)
pythondocker script.py --verbose

# Пересоздание окружения
pythondocker script.py --force-recreate

# PyPy (JIT-компиляция, при загрузке показывается прогресс)
pythondocker script.py --python pypy3.11

# Jython (требует Java)
pythondocker script.py --python jython

# Режим offline (только установленные версии)
pythondocker script.py --python 3.11 --offline

# Shell-автодополнение
source <(pythondocker completions bash)

# Подробная справка
pythondocker help
```

### Альтернативные интерпретаторы (PyPy, Jython)

PythonDocker поддерживает альтернативные интерпретаторы Python:

| Интерпретатор | Версии | Описание |
|---------------|--------|----------|
| **PyPy** | pypy3.11, pypy3.10, pypy3.9, pypy2.7 | JIT-компиляция, часто быстрее CPython. |
| **Jython** | jython | Python на JVM. Требует установленной Java (`java -version`). |

Архивы PyPy и Jython кэшируются в `~/.pythondocker/cache/` — при переустановке не перекачиваются.

```bash
# PyPy — быстрый JIT-интерпретатор
pythondocker script.py --python pypy3.11

# Jython — Python на Java
pythondocker script.py --python jython -r requirements.txt

# Удаление альтернативных интерпретаторов
pythondocker remove pypy3.11
pythondocker remove jython
```

### Параметры командной строки

| Параметр | Краткая форма | Описание |
|----------|---------------|----------|
| `--python` | `-p` | Версия Python (2.7, 3.11, pypy3.11, jython) |
| `--requirements` | `-r` | Путь к файлу requirements.txt |
| `--args` | - | Аргументы, передаваемые скрипту |
| `--env` | - | Переменные окружения в формате KEY=VALUE |
| `--encoding` | `-e` | Кодировка для запуска скрипта (utf-8, cp1251, cp866 и др.) |
| `--version` | `-v` | Показать версию и URL репозитория (github.com/thenola/pythondocker) |
| `--verbose` | - | Подробный вывод |
| `--force-recreate` | - | Пересоздать окружение если оно уже существует |
| `--no-deps` | - | Не устанавливать зависимости из requirements.txt |
| `--shell` | - | Запустить интерактивный Python shell в окружении |
| `--log-file` | `-l` | Записать вывод (stdout и stderr) в файл |
| `--debug` | `-d` | Показать служебные сообщения (создание окружения, версия Python и т.д.) |
| `--offline` | - | Только уже установленные версии, не скачивать |
| `--docker` | - | Запустить в Docker-контейнере (python:X-slim) вместо venv |

## Конфигурация (.pythondocker.yml / .pythondocker.json)

Создайте файл в корне проекта, чтобы не указывать флаги при каждом запуске:

```yaml
# .pythondocker.yml (требует PyYAML: pip install PyYAML)
python: "3.11"              # или default_interpreter
requirements: "requirements.txt"
encoding: "cp1251"
docker: false               # true — использовать Docker вместо venv
env:
  DEBUG: "true"
  API_KEY: "secret"
# PyPy: опции JIT
pypy_jit_options: "trace_limit=1000"
# Jython: опции JVM
java_opts: "-Xmx1g"
```

```json
// .pythondocker.json (работает без доп. зависимостей)
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

Конфиг ищется в директории скрипта и родительских директориях. Параметры из CLI переопределяют значения из конфига. 

**Для поддержки YAML формата установите:** 
```bash
pip install PyYAML 
# или при установке пакета:
pip install python-docker-package[yaml]
```

Опция `docker: true` в конфиге включает запуск в Docker по умолчанию.

## Интеграция с Docker

С флагом `--docker` скрипт выполняется в Docker-контейнере вместо venv. Требуется установленный и запущенный Docker.

**Поддерживаемые образы:** `python:2.7-slim`, `python:3.8-slim` … `python:3.13-slim`, `pypy:2.7-slim`, `pypy:3.10-slim`, `pypy:3.11-slim`.

```bash
# Запуск скрипта в контейнере
pythondocker script.py --docker

# Python 3.11 + requirements.txt
pythondocker script.py --python 3.11 --docker -r requirements.txt

# Интерактивный shell в контейнере
pythondocker --shell --python 3.11 --docker
```

Рабочая директория монтируется в `/work` в контейнере. `requirements.txt` устанавливается перед запуском. Jython в режиме Docker не поддерживается. Проверка: `pythondocker info` — показывает «Docker доступен: Да/Нет».

## Примеры

### Пример 1: Запуск Python 2 скрипта

Создайте файл `old_script.py`:

```python
#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
print "Hello from Python 2.7!"
```

Запустите:

```bash
pythondocker old_script.py
```

PythonDocker автоматически определит версию Python 2.7 из shebang и запустит скрипт.

### Пример 2: Запуск с зависимостями

Создайте файл `requirements.txt`:

```txt
requests==2.28.0
numpy==1.21.0
```

Запустите:

```bash
pythondocker script.py --requirements requirements.txt
```

Программа автоматически установит зависимости в изолированное окружение.

### Пример 3: Запуск с аргументами и переменными окружения

```bash
pythondocker process_data.py --args input.txt output.txt --env DEBUG=true API_KEY=secret123
```

### Пример 4: Работа с кодировкой CP1251 (Windows)

```bash
pythondocker script.py --python 2.7 --encoding cp1251
```

### Пример 5: Указание версии Python вручную

```bash
pythondocker script.py --python 3.9
```

### Пример 6: Запуск Jupyter Notebook

```bash
pythondocker notebook.ipynb
```

Notebook конвертируется в Python-скрипт и выполняется. По умолчанию используется Python 3.11.

### Пример 7: Запуск без установки зависимостей

```bash
pythondocker script.py --no-deps
```

Полезно, если зависимости уже установлены и нужно ускорить запуск.

### Пример 8: Интерактивный Python shell

```bash
pythondocker --shell
pythondocker --shell --python 2.7
```

Запускает интерактивную оболочку Python в изолированном окружении.

### Пример 9: Режим offline и Shell-автодополнение

```bash
# Запуск в Docker-контейнере
pythondocker script.py --docker
pythondocker script.py --python 3.11 --docker -r requirements.txt

# Режим offline — только уже установленные версии
pythondocker script.py --python 3.11 --offline

# Автодополнение для bash/zsh/PowerShell
source <(pythondocker completions bash)   # bash
source <(pythondocker completions zsh)    # zsh
pythondocker completions powershell | Out-String | Invoke-Expression  # PowerShell
```

### Пример 10: Запись вывода в файл

```bash
pythondocker script.py --log-file output.log
```

Сохраняет весь вывод (stdout и stderr) в указанный файл.

### Пример 11: Режим отладки (-d / --debug)

```bash
pythondocker script.py -d
```

Показывает служебные сообщения (создание окружения, версия Python, кодировка и т.п.). По умолчанию эти сообщения скрыты.

## Архитектура

### Как работает PythonDocker

1. **Определение версии Python**:
   - Проверка shebang строки (`#!/usr/bin/env python2.7`)
   - Поиск комментариев с указанием версии (`# Requires Python 2.7`)
   - Анализ синтаксиса (поиск признаков Python 2: `print` без скобок, `xrange()`, `raw_input()` и др.)

2. **Подготовка окружения**:
   - Проверка наличия нужной версии Python локально
   - Скачивание версии с python.org (если отсутствует)
   - Создание изолированного виртуального окружения
   - Установка зависимостей из `requirements.txt` (если указан)

3. **Запуск скрипта**:
   - Запуск скрипта в изолированном виртуальном окружении
   - Использование правильной версии Python
   - Передача аргументов и переменных окружения
   - Настройка кодировки для ввода/вывода

4. **Хранение данных**:
   - Версии Python хранятся в `~/.pythondocker/python/`
   - Виртуальные окружения создаются в `~/.pythondocker/envs/`
   - Окружения переиспользуются между запусками

### Определение версии Python

PythonDocker определяет версию Python следующими способами (в порядке приоритета):

1. **Shebang строка**: `#!/usr/bin/env python2.7`
2. **Комментарии**: `# Requires Python 2.7`, `# Python version: 2.7`
3. **Анализ синтаксиса**: поиск признаков Python 2:
   - `print` без скобок
   - `xrange()` вместо `range()`
   - `dict.iteritems()`, `dict.iterkeys()`, `dict.itervalues()`
   - `raw_input()` вместо `input()`
   - `unicode()` функция
   - `basestring` тип
   - и другие характерные конструкции

4. **По умолчанию**: если версия не определена, используется Python 3.11

## Поддерживаемые версии Python

PythonDocker поддерживает все версии Python, доступные на python.org:

- **Python 2.x**: 2.7 (последняя версия Python 2)
- **Python 3.x**: 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13+

Программа автоматически скачивает нужную версию для вашей платформы (Windows, Linux, macOS).

## Управление окружениями

Команды: `list`, `info`, `clean`, `remove`, `freeze`, `completions`, `help`.

### Просмотр списка окружений

```bash
pythondocker list
```

Выводит список всех созданных окружений с информацией о версии Python и размере.

### Информация о системе

```bash
pythondocker info
```

Показывает:
- Количество установленных версий Python
- Количество созданных окружений
- Пути к директориям
- Доступность pyenv и Docker

### Очистка окружений

```bash
# Просмотр того, что будет удалено (dry-run)
pythondocker clean --dry-run

# Удаление неиспользуемых окружений
pythondocker clean
```

### Удаление версии Python

```bash
# Просмотр того, что будет удалено (dry-run)
pythondocker remove 2.7 --dry-run

# Удаление конкретной версии Python
pythondocker remove 2.7
```

### Подробная справка

```bash
pythondocker help
```

Выводит полное руководство (MANUAL.md).

### Генерация requirements.txt (pip freeze)

```bash
# Из текущего Python (окружение, где запущен pythondocker)
pythondocker freeze --current -o requirements.txt

# Из окружения PythonDocker (версия 3.11)
pythondocker freeze --python 3.11 -o requirements.txt

# Версия определяется из скрипта
pythondocker freeze script.py -o requirements.txt

# Вывод в stdout
pythondocker freeze --current
```

## Интеграция с IDE

PythonDocker можно запускать прямо из IDE.

### Visual Studio Code

1. Скопируйте `.ide/vscode/tasks.json` в `.vscode/` вашего проекта
2. Нажмите **Ctrl+Shift+B** (или Cmd+Shift+B на macOS) для запуска текущего файла

### PyCharm

1. **Settings** → **Tools** → **External Tools** → **+**
2. Name: `PythonDocker`, Program: `pythondocker`, Arguments: `$FilePath$`, Working: `$FileDir$`
3. Запуск: правый клик по файлу → **External Tools** → **PythonDocker**

Подробные инструкции: [.ide/README.md](.ide/README.md)

## Решение проблем

### Python не скачивается

Если версия Python не скачивается:

1. Проверьте подключение к интернету
2. Убедитесь, что у вас достаточно места на диске
3. Проверьте права доступа к директории `~/.pythondocker/`
4. Используйте флаг `--verbose` для подробного вывода

### Версия Python не найдена

Если программа не может найти нужную версию Python:

1. Программа автоматически попытается скачать её с python.org
2. Если скачивание не удалось, проверьте доступность версии для вашей платформы
3. Для некоторых старых версий может потребоваться ручная установка
4. Используйте `pythondocker info` для просмотра установленных версий

### Скрипт не запускается

Если скрипт не запускается:

1. Используйте флаг `--verbose` для подробного вывода
2. Проверьте, что скрипт существует и доступен для чтения
3. Убедитесь, что версия Python указана правильно
4. Проверьте синтаксис скрипта

### Проблемы с кодировкой

Для работы с файлами в кодировке CP1251 (Windows):

```bash
pythondocker script.py --python 2.7 --encoding cp1251
```

Программа автоматически определит кодировку из комментария `# -*- coding: ... -*-` в начале файла.

### Docker недоступен

- Убедитесь, что Docker установлен и демон запущен: `docker info`
- Используйте режим без `--docker` (venv)

### Проблемы с зависимостями

Если зависимости не устанавливаются:

1. Проверьте формат файла `requirements.txt`
2. Убедитесь, что версия Python поддерживает нужные пакеты
3. Используйте `--verbose` для просмотра ошибок установки
4. Попробуйте пересоздать окружение с `--force-recreate`

## Разработка

### Установка в режиме разработки

```bash
git clone https://github.com/thenola/pythondocker.git
cd pythondocker
pip install -e .
```

### Структура проекта

```
pythondocker/
├── pythondocker/
│   ├── __init__.py              # Версия пакета
│   ├── cli.py                   # CLI интерфейс
│   ├── commands.py              # Команды list, info, clean, remove, freeze
│   ├── config_loader.py         # .pythondocker.yml / .pythondocker.json
│   ├── version_detector.py      # Определение версии Python
│   ├── python_installer.py      # Скачивание версий Python
│   ├── environment_manager.py   # Управление venv-окружениями
│   ├── docker_runner.py         # Запуск в Docker
│   ├── notebook_runner.py       # Конвертация .ipynb в .py
│   ├── pyenv_manager.py         # Интеграция с pyenv
│   └── MANUAL.md                # Подробная справка
├── completions/                 # Автодополнение bash, zsh, powershell
├── examples/                    # Примеры
├── tests/                       # Юнит- и интеграционные тесты
├── setup.py
├── MANUAL.md
└── README.md
```

### Запуск тестов

```bash
# Все тесты (юнит + интеграционные)
python tests/run_all_tests.py

# Только юнит-тесты
python -m unittest tests.test_version_detector tests.test_config_loader tests.test_docker_runner -v

# Интеграционный тест
pythondocker tests/test_python2.py --python 2.7
```

### Вклад в проект

Приветствуются pull requests и issues! Пожалуйста:

1. Создайте форк репозитория
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).

```
MIT License

Copyright (c) 2024 PythonDocker Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
