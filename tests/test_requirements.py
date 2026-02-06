# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки установки зависимостей
Требует установки библиотеки requests
"""

try:
    import requests
    print("Библиотека requests успешно импортирована!")
    # Совместимость с Python 2 и 3
    try:
        version = requests.__version__
    except:
        version = "неизвестна"
    print("Версия requests: %s" % version)
except ImportError:
    print("ОШИБКА: Библиотека requests не установлена!")
    print("Запустите: pythondocker test_requirements.py --requirements requirements_test.txt")
    import sys
    sys.exit(1)

print("\nТест зависимостей завершен успешно!")
