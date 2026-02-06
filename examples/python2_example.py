#!/usr/bin/env python2.7
# Пример скрипта на Python 2.7

print "Hello from Python 2.7!"
print "This script uses Python 2 syntax"

# Python 2 особенности
items = {'a': 1, 'b': 2, 'c': 3}
for key, value in items.iteritems():
    print "%s: %s" % (key, value)

# Использование xrange
for i in xrange(5):
    print "Number:", i

# raw_input вместо input
# name = raw_input("Enter your name: ")
# print "Hello,", name
