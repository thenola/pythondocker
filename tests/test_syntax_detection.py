# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки определения версии Python по синтаксису
Не содержит явных указаний версии, только синтаксические признаки
"""

# Использование print без скобок (Python 2)
print "Тест определения версии по синтаксису"

# Использование xrange (Python 2)
for i in xrange(3):
    print "Итерация %d" % i

# Использование dict.iteritems() (Python 2)
data = {'key1': 'value1', 'key2': 'value2'}
for key, value in data.iteritems():
    print "%s: %s" % (key, value)

# Использование raw_input (Python 2)
# name = raw_input("Введите имя: ")
# print "Привет, %s!" % name

print "Тест завершен!"
