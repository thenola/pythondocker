# Быстрый старт

## Установка

```bash
pip install -e .
```

## Первое использование

1. **Docker НЕ требуется!** Программа работает самостоятельно
2. При первом запуске программа автоматически скачает нужную версию Python
3. Запустите пример скрипта:

```bash
pythondocker examples/python2_example.py
```

Или создайте свой скрипт:

```python
# my_script.py
#!/usr/bin/env python2.7
print "Hello World!"
```

И запустите:

```bash
pythondocker my_script.py
```

## Основные команды

```bash
# Автоматическое определение версии
pythondocker script.py

# Указать версию вручную
pythondocker script.py --python 2.7

# С зависимостями
pythondocker script.py --requirements req.txt

# С аргументами
pythondocker script.py --args arg1 arg2
```

Подробнее см. `USAGE_RU.md` или `README.md`
