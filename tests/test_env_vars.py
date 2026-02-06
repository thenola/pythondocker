# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки переменных окружения
"""

import os

print("Тест переменных окружения")
print("=" * 40)

# Проверка стандартных переменных
print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'не установлена')}")

# Проверка пользовательских переменных
test_var = os.environ.get('TEST_VAR', 'не установлена')
print(f"TEST_VAR: {test_var}")

debug = os.environ.get('DEBUG', 'не установлена')
print(f"DEBUG: {debug}")

print("\nИспользование:")
print("  pythondocker test_env_vars.py --env TEST_VAR=test_value DEBUG=true")

print("\nТест завершен!")
