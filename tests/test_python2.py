# -*- coding: utf-8 -*-
#!/usr/bin/env python2.7
"""
Тестовый скрипт для Python 2.7
Проверяет базовые возможности Python 2
"""

print "Тест Python 2.7"
print "=" * 40

# Проверка print без скобок
name = "PythonDocker"
print "Привет, %s!" % name

# Проверка деления целых чисел (Python 2)
a = 10
b = 3
result = a / b
print "Результат деления (Python 2): %d" % result

# Проверка float деления
result_float = float(a) / b
print "Результат float деления: %.2f" % result_float

# Проверка словарей
items = {'a': 1, 'b': 2, 'c': 3}
print "\nИтерация по словарю (Python 2):"
for key, value in items.iteritems():
    print "  %s: %s" % (key, value)

# Проверка xrange
print "\nИспользование xrange:"
for i in xrange(5):
    print "  Число: %d" % i

# Проверка unicode (для Python 2 нужно правильно обрабатывать)
try:
    text = u"Тест Unicode"
    # Используем encode для вывода Unicode в Python 2
    print "\nUnicode строка: %s" % text.encode('utf-8')
except UnicodeEncodeError:
    # Если не удалось закодировать, просто выводим как есть
    print "\nUnicode строка: Тест Unicode"

print "\nТест завершен успешно!"
