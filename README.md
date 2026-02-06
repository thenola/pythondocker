# PythonDocker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

**PythonDocker** — инструмент для запуска старых Python скриптов (включая Python 2.x) в изолированных виртуальных окружениях с автоматическим определением версии Python. Работает без Docker, используя только стандартную библиотеку Python.

## Содержание

- [Описание](#описание)
- [Возможности](#возможности)
- [Требования](#требования)
- [Установка](#установка)
- [Использование](#использование)
- [Примеры](#примеры)
- [Архитектура](#архитектура)
- [Поддерживаемые версии Python](#поддерживаемые-версии-python)
- [Управление окружениями](#управление-окружениями)
- [Решение проблем](#решение-проблем)
- [Разработка](#разработка)
- [Лицензия](#лицензия)
- [Авторы](#авторы)

## Описание

PythonDocker решает проблему запуска устаревших Python скриптов, которые требуют специфических версий Python (например, Python 2.7). Программа автоматически:

- Определяет необходимую версию Python из скрипта
- Скачивает и устанавливает нужную версию Python (если отсутствует)
- Создает изолированное виртуальное окружение
- Устанавливает зависимости из `requirements.txt`
- Запускает скрипт в изолированном окружении

**Важно**: PythonDocker не использует Docker. Вместо этого применяются виртуальные окружения Python и автоматическое управление версиями интерпретатора.

## Возможности

- **Автоматическое определение версии Python** — анализ shebang, комментариев и синтаксиса
- **Изоляция через виртуальные окружения** — каждый скрипт запускается в отдельном окружении
- **Автоматическая установка зависимостей** — поддержка `requirements.txt`
- **Автоматическое скачивание Python** — загрузка нужных версий с python.org
- **Поддержка кодировок** — автоматическое определение и управление кодировками (UTF-8, CP1251, CP866 и др.)
- **Простой CLI интерфейс** — интуитивно понятные команды
- **Работает без Docker** — использует только стандартную библиотеку Python
- **Кроссплатформенность** — поддержка Windows, Linux и macOS
- **Управление окружениями** — команды для просмотра, очистки и удаления окружений

## Требования

- **Python 3.7+** (для запуска программы PythonDocker)
- **Доступ к интернету** (для скачивания версий Python при первом использовании)
- **Место на диске** (~100-200 МБ на версию Python)
- **Docker НЕ требуется**

## Установка

### Установка из исходников

```bash
# Клонируйте репозиторий
git clone https://github.com/thenola/pythondocker.git
cd pythondocker

# Установите пакет в режиме разработки
pip install -e .

# Или выполните обычную установку
python setup.py install
```

### Установка через pip (если доступно)

```bash
pip install pythondocker
```

После установки команда `pythondocker` будет доступна в командной строке.

**Примечание**: При первом запуске программа автоматически скачает нужную версию Python, если она отсутствует локально.

## Использование

### Базовое использование

```bash
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
```

### Параметры командной строки

| Параметр | Краткая форма | Описание |
|----------|---------------|----------|
| `--python` | `-p` | Версия Python (например, 2.7, 3.11) |
| `--requirements` | `-r` | Путь к файлу requirements.txt |
| `--args` | - | Аргументы для передаваемые скрипту |
| `--env` | - | Переменные окружения в формате KEY=VALUE |
| `--encoding` | `-e` | Кодировка для запуска скрипта (utf-8, cp1251, cp866 и др.) |
| `--verbose` | `-v` | Подробный вывод |
| `--force-recreate` | - | Пересоздать окружение если оно уже существует |

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

PythonDocker предоставляет команды для управления окружениями:

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
- Доступность pyenv

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
│   ├── __init__.py              # Инициализация пакета
│   ├── cli.py                   # CLI интерфейс
│   ├── commands.py              # Команды управления окружениями
│   ├── version_detector.py      # Определение версии Python
│   ├── python_installer.py      # Скачивание и установка версий Python
│   ├── environment_manager.py  # Управление виртуальными окружениями
│   └── pyenv_manager.py        # Интеграция с pyenv (опционально)
├── examples/                    # Примеры скриптов
│   ├── python2_example.py
│   ├── python3_example.py
│   └── requirements_example.txt
├── tests/                       # Тесты
│   ├── test_python2.py
│   ├── test_python3.py
│   ├── test_encoding_cp1251.py
│   └── ...
├── setup.py                     # Установочный файл
├── requirements.txt             # Зависимости (пустой - используется только stdlib)
└── README.md                    # Документация
```

### Запуск тестов

```bash
# Запуск всех тестов
python tests/run_all_tests.py

# Запуск конкретного теста
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

## Авторы

- **thenola** - [GitHub](https://github.com/thenola)

---

**GitHub**: [thenola/pythondocker](https://github.com/thenola/pythondocker)

**Лицензия**: MIT


