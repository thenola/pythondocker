# Заметки по тестированию

## Известные проблемы и решения

### 1. Embeddable Python 3.11 не поддерживает venv

**Проблема:** Embeddable версии Python не содержат модуль venv, поэтому создание виртуального окружения через venv не работает.

**Решение:** 
- Программа автоматически определяет, поддерживает ли Python модуль venv
- Если venv не поддерживается, создается простое окружение
- Рекомендуется использовать системный Python 3 для лучшей совместимости

**Как проверить:**
```bash
# Используйте системный Python 3
pythondocker tests/test_python3.py
```

### 2. Кодировка cp1251

**Проблема:** Файлы в кодировке cp1251 могут неправильно читаться при определении версии Python.

**Решение:**
- Программа пытается определить кодировку из комментария `# -*- coding: ... -*-`
- Используется несколько методов декодирования для поиска комментария
- При запуске скрипта устанавливается правильная кодировка через PYTHONIOENCODING

**Как проверить:**
```bash
pythondocker tests/test_encoding_cp1251.py --python 2.7 --encoding cp1251
```

### 3. Unicode в Python 2

**Проблема:** Python 2 требует явной обработки Unicode строк при выводе.

**Решение:**
- В тестовых скриптах добавлена обработка Unicode через codecs
- Программа устанавливает PYTHONIOENCODING с параметром :replace для обработки ошибок

### 4. Путь к requirements.txt

**Проблема:** Относительные пути к requirements.txt могут не находиться.

**Решение:**
- Программа автоматически ищет файл относительно директории скрипта
- Также проверяется текущая рабочая директория
- Используйте абсолютные пути для надежности

**Как проверить:**
```bash
# Из директории tests
pythondocker test_requirements.py --requirements requirements_test.txt

# Из другой директории
pythondocker tests/test_requirements.py --requirements tests/requirements_test.txt
```

## Рекомендации по запуску тестов

1. **Для Python 2 тестов:** Убедитесь, что Python 2.7 установлен в системе или доступен через pyenv
2. **Для Python 3 тестов:** Используйте системный Python 3 (не embeddable версию)
3. **Для тестов с кодировкой:** Убедитесь, что консоль поддерживает нужную кодировку
4. **Для тестов зависимостей:** Убедитесь, что есть доступ к интернету для установки пакетов

## Запуск отдельных тестов

```bash
# Python 2 тест
pythondocker tests/test_python2.py --python 2.7

# Python 3 тест (используйте системный Python)
pythondocker tests/test_python3.py

# Тест кодировки
pythondocker tests/test_encoding_cp1251.py --python 2.7 --encoding cp1251

# Тест зависимостей
pythondocker tests/test_requirements.py --requirements tests/requirements_test.txt

# Тест аргументов
pythondocker tests/test_args.py --args arg1 arg2 arg3

# Тест переменных окружения
pythondocker tests/test_env_vars.py --env TEST_VAR=value DEBUG=true
```
