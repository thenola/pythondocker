# Быстрая инструкция по публикации на PyPI

## Шаг 1: Установка инструментов

```bash
pip install --upgrade build twine
```

## Шаг 2: Регистрация на PyPI

1. Зарегистрируйтесь на [pypi.org](https://pypi.org/account/register/)
2. Создайте API токен: Account settings → API tokens → Add API token
3. Скопируйте токен (начинается с `pypi-`)

## Шаг 3: Проверка имени пакета

**ВАЖНО**: Проверьте, что имя `pythondocker` свободно:
- Откройте [pypi.org/project/pythondocker](https://pypi.org/project/pythondocker)
- Если имя занято, измените `name` в `setup.py`

## Шаг 4: Сборка и публикация

### Вариант A: Использование скрипта (рекомендуется)

```bash
# Сборка пакета
python publish.py build

# Проверка пакета
python publish.py check

# Тестовая публикация на TestPyPI
python publish.py testpypi
# Введите username: __token__
# Введите password: ваш_токен

# Публикация на PyPI
python publish.py pypi
# Введите username: __token__
# Введите password: ваш_токен
```

### Вариант B: Ручная публикация

```bash
# Очистка старых сборок
rm -rf build dist *.egg-info
# Windows: rmdir /s /q build dist *.egg-info

# Сборка
python -m build

# Проверка
python -m twine check dist/*

# Публикация на TestPyPI (для тестирования)
python -m twine upload --repository testpypi dist/*

# Публикация на PyPI
python -m twine upload dist/*
```

## Шаг 5: Проверка

```bash
pip install pythondocker
pythondocker --help
```

## Обновление версии

1. Измените версию в `pythondocker/__init__.py`
2. Повторите шаг 4

---

Подробная инструкция: см. [PUBLISH.md](PUBLISH.md)
