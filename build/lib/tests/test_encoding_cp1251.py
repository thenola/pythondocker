# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки кодировки cp1251
Содержит русские символы
ПРИМЕЧАНИЕ: Файл сохранен в UTF-8, но тестирует работу с кодировкой cp1251
"""

import sys

# Устанавливаем кодировку для вывода (cp1251 для Windows) ПЕРЕД первым выводом
if sys.version_info[0] < 3:
    import codecs
    # Пробуем установить cp1251 для вывода
    try:
        sys.stdout = codecs.getwriter('cp1251')(sys.stdout, 'replace')
        sys.stderr = codecs.getwriter('cp1251')(sys.stderr, 'replace')
    except Exception:
        # Если cp1251 не доступна, используем UTF-8
        try:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'replace')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr, 'replace')
        except Exception:
            pass  # Используем стандартный вывод

# Используем unicode строки для Python 2.7
if sys.version_info[0] < 3:
    print u"Тест кодировки cp1251"
    print u"=" * 40
else:
    print("Тест кодировки cp1251")
    print("=" * 40)

# Русский текст
try:
    # Пробуем использовать Unicode строку
    if sys.version_info[0] < 3:
        text = u"Привет из Python 2!"
        # Пробуем вывести в cp1251
        try:
            print text.encode('cp1251', 'replace')
        except Exception:
            # Если не получается, пробуем UTF-8
            try:
                print text.encode('utf-8', 'replace')
            except Exception:
                print text
    else:
        text = "Привет из Python 2!"
        print(text)
except Exception as e:
    if sys.version_info[0] < 3:
        print u"Ошибка при выводе текста: %s" % unicode(e)
        print u"Привет из Python 2!"  # Fallback
    else:
        print("Ошибка при выводе текста: %s" % str(e))
        print("Привет из Python 2!")  # Fallback

# Проверка работы с русскими символами
try:
    if sys.version_info[0] < 3:
        names = [u"Иван", u"Мария", u"Петр"]
    else:
        names = ["Иван", "Мария", "Петр"]
    
    if sys.version_info[0] < 3:
        print u"\nСписок имен:"
    else:
        print("\nСписок имен:")
    for name in names:
        if sys.version_info[0] < 3:
            try:
                name_str = name.encode('cp1251', 'replace')
                print "  - %s" % name_str
            except Exception:
                try:
                    name_str = name.encode('utf-8', 'replace')
                    print "  - %s" % name_str
                except Exception:
                    print "  - %s" % name
        else:
            print("  - %s" % name)
except Exception as e:
    if sys.version_info[0] < 3:
        print u"\nОшибка при выводе имен: %s" % unicode(e)
    else:
        print("\nОшибка при выводе имен: %s" % str(e))

if sys.version_info[0] < 3:
    print u"\nТест кодировки завершен!"
else:
    print("\nТест кодировки завершен!")
