# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Тестовый скрипт для Python 3
Проверяет базовые возможности Python 3
"""

print("Тест Python 3")
print("=" * 40)

# Проверка print с скобками
name = "PythonDocker"
print(f"Привет, {name}!")

# Проверка деления (Python 3 всегда float)
a = 10
b = 3
result = a / b
print(f"Результат деления (Python 3): {result:.2f}")

# Проверка целочисленного деления
result_int = a // b
print(f"Результат целочисленного деления: {result_int}")

# Проверка словарей
items = {'a': 1, 'b': 2, 'c': 3}
print("\nИтерация по словарю (Python 3):")
for key, value in items.items():
    print(f"  {key}: {value}")

# Проверка range
print("\nИспользование range:")
for i in range(5):
    print(f"  Число: {i}")

# Проверка f-strings
text = "Тест f-strings"
print(f"\nF-string: {text}")

print("\nТест завершен успешно!")
