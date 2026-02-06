# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки работы с файлами
"""

import os
import tempfile

print("Тест работы с файлами")
print("=" * 40)

# Создаем временный файл
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
    test_file = f.name
    f.write("Тестовая строка 1\n")
    f.write("Тестовая строка 2\n")
    f.write("Тестовая строка 3\n")

print(f"Создан временный файл: {test_file}")

# Читаем файл
try:
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"\nСодержимое файла ({len(content)} символов):")
        print(content)
    
    # Проверяем количество строк
    lines = content.strip().split('\n')
    print(f"Количество строк: {len(lines)}")
    
    print("\n✓ Чтение файла успешно")
except Exception as e:
    print(f"\n✗ Ошибка при чтении файла: {e}")

# Удаляем временный файл
try:
    os.unlink(test_file)
    print("✓ Временный файл удален")
except Exception as e:
    print(f"✗ Ошибка при удалении файла: {e}")

print("\nТест завершен!")
