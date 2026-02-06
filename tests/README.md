# Тестовые скрипты для PythonDocker

Эта папка содержит тестовые скрипты для проверки функциональности PythonDocker.

## Тестовые файлы

### test_python2.py
Тестовый скрипт для Python 2.7. Проверяет:
- print без скобок
- Деление целых чисел
- dict.iteritems()
- xrange()
- Unicode строки

**Запуск:**
```bash
pythondocker tests/test_python2.py --python 2.7
```

### test_python3.py
Тестовый скрипт для Python 3. Проверяет:
- print с скобками
- Деление (всегда float)
- dict.items()
- range()
- f-strings

**Запуск:**
```bash
pythondocker tests/test_python3.py
```

### test_encoding_cp1251.py
Тестовый скрипт для проверки кодировки cp1251 (Windows, русские символы).

**Запуск:**
```bash
pythondocker tests/test_encoding_cp1251.py --python 2.7 --encoding cp1251
```

### test_requirements.py
Тестовый скрипт для проверки установки зависимостей из requirements.txt.

**Запуск:**
```bash
pythondocker tests/test_requirements.py --requirements tests/requirements_test.txt
```

### test_args.py
Тестовый скрипт для проверки передачи аргументов скрипту.

**Запуск:**
```bash
pythondocker tests/test_args.py --args arg1 arg2 arg3
```

### test_env_vars.py
Тестовый скрипт для проверки переменных окружения.

**Запуск:**
```bash
pythondocker tests/test_env_vars.py --env TEST_VAR=test_value DEBUG=true
```

### test_syntax_detection.py
Тестовый скрипт для проверки автоматического определения версии Python по синтаксису (без явных указаний версии).

**Запуск:**
```bash
pythondocker tests/test_syntax_detection.py
```

## Запуск всех тестов

Для запуска всех тестов можно использовать скрипт `run_all_tests.py`:

```bash
# Автоматический запуск всех тестов
python tests/run_all_tests.py

# Или вручную через цикл:
# Windows
for %f in (tests\test_*.py) do pythondocker %f

# Linux/macOS
for f in tests/test_*.py; do pythondocker "$f"; done
```

Скрипт `run_all_tests.py` автоматически:
- Определяет параметры для каждого теста
- Запускает тесты с правильными флагами
- Выводит итоговую статистику

## Требования

- PythonDocker должен быть установлен
- Для test_requirements.py нужен файл requirements_test.txt
- Для test_encoding_cp1251.py нужна поддержка кодировки cp1251 (Windows)
