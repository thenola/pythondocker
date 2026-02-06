# Инструкция по публикации на PyPI

Это руководство поможет вам опубликовать PythonDocker на PyPI.

## Предварительные требования

1. **Аккаунт на PyPI**: Зарегистрируйтесь на [pypi.org](https://pypi.org/account/register/)
2. **API токен**: Создайте API токен в настройках аккаунта PyPI
   - Перейдите в Account settings → API tokens
   - Создайте новый токен с правами на весь проект или только для `pythondocker`
3. **Инструменты для сборки**: Установите необходимые пакеты

```bash
pip install --upgrade build twine
```

## Проверка перед публикацией

### 1. Проверьте имя пакета

Убедитесь, что имя `pythondocker` свободно на PyPI:
- Проверьте на [pypi.org/project/pythondocker](https://pypi.org/project/pythondocker)
- Если имя занято, измените `name` в `setup.py`

### 2. Проверьте версию

Убедитесь, что версия в `setup.py` и `pythondocker/__init__.py` совпадает и уникальна.

### 3. Проверьте метаданные

Проверьте, что все поля в `setup.py` заполнены корректно:
- `name` - имя пакета
- `version` - версия
- `description` - краткое описание
- `author` - автор
- `url` - URL проекта
- `license` - лицензия (указана в classifiers)

### 4. Проверьте файлы

Убедитесь, что важные файлы включены:
- `LICENSE` - лицензия
- `README.md` - документация
- Все файлы Python из пакета `pythondocker/`

## Сборка пакета

### 1. Очистка старых сборок

```bash
# Удалите старые сборки
rm -rf build/ dist/ *.egg-info
# На Windows:
rmdir /s /q build dist *.egg-info
```

### 2. Сборка дистрибутивов

```bash
# Сборка исходного дистрибутива и wheel
python -m build
```

Это создаст файлы в директории `dist/`:
- `pythondocker-1.0.0.tar.gz` - исходный дистрибутив
- `pythondocker-1.0.0-py3-none-any.whl` - wheel файл

### 3. Проверка сборки

```bash
# Проверка дистрибутивов
python -m twine check dist/*
```

## Тестирование на TestPyPI

**Рекомендуется**: Сначала опубликуйте на TestPyPI для проверки.

### 1. Регистрация на TestPyPI

Зарегистрируйтесь на [test.pypi.org](https://test.pypi.org/account/register/)

### 2. Создайте API токен для TestPyPI

Создайте токен в настройках TestPyPI аккаунта.

### 3. Публикация на TestPyPI

```bash
# Публикация на TestPyPI
python -m twine upload --repository testpypi dist/*
```

Вам будет предложено ввести:
- Username: `__token__`
- Password: ваш API токен (начинается с `pypi-`)

### 4. Проверка установки с TestPyPI

```bash
# Установка с TestPyPI для проверки
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pythondocker
```

## Публикация на PyPI

### Вариант 1: Использование API токена (рекомендуется)

```bash
# Публикация на PyPI
python -m twine upload dist/*
```

Введите:
- Username: `__token__`
- Password: ваш API токен PyPI (начинается с `pypi-`)

### Вариант 2: Использование .pypirc (альтернатива)

Создайте файл `~/.pypirc` (или `C:\Users\YourName\.pypirc` на Windows):

```ini
[pypi]
username = __token__
password = pypi-ваш_токен_здесь

[testpypi]
username = __token__
password = pypi-ваш_тестовый_токен_здесь
```

Затем используйте:

```bash
python -m twine upload dist/*
```

### Вариант 3: Использование переменных окружения

```bash
# Linux/macOS
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-ваш_токен_здесь
python -m twine upload dist/*

# Windows PowerShell
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-ваш_токен_здесь"
python -m twine upload dist/*
```

## Проверка после публикации

1. Проверьте страницу пакета: [pypi.org/project/pythondocker](https://pypi.org/project/pythondocker)
2. Проверьте установку:

```bash
pip install pythondocker
pythondocker --help
```

## Обновление версии

При обновлении пакета:

1. Обновите версию в `pythondocker/__init__.py`:
   ```python
   __version__ = "1.0.1"
   ```

2. Обновите версию в `setup.py` (или она подхватится автоматически)

3. Обновите `CHANGELOG.md` с описанием изменений

4. Повторите процесс сборки и публикации

## Автоматизация с GitHub Actions (опционально)

Вы можете настроить автоматическую публикацию при создании тега. Создайте `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: python -m twine upload dist/*
```

## Решение проблем

### Ошибка: "Package already exists"

Если пакет с такой версией уже существует, увеличьте версию в `setup.py` и `__init__.py`.

### Ошибка: "Invalid distribution"

Проверьте, что все файлы включены правильно. Убедитесь, что `MANIFEST.in` содержит нужные файлы.

### Ошибка аутентификации

- Убедитесь, что используете правильный токен
- Проверьте, что токен имеет права на публикацию
- Убедитесь, что используете `__token__` как username

## Полезные ссылки

- [PyPI Documentation](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)
