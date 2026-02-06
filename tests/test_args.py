# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки передачи аргументов
"""

import sys

print("Тест передачи аргументов")
print("=" * 40)

print(f"Количество аргументов: {len(sys.argv)}")
print(f"Аргументы: {sys.argv}")

if len(sys.argv) > 1:
    print("\nПереданные аргументы:")
    for i, arg in enumerate(sys.argv[1:], 1):
        print(f"  {i}. {arg}")
else:
    print("\nАргументы не переданы")
    print("Использование: pythondocker test_args.py --args arg1 arg2 arg3")

print("\nТест завершен!")
