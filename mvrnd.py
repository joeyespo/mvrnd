from __future__ import print_function

import re
import os
import sys
import shutil
import random
from datetime import datetime


WEEKDAYS = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']


def is_special(filename):
    return filename.startswith('(') and filename.endswith(')')


def move_random_file(from_path, to_path, delete_empty=False):
    print('Moving a random file...')

    filenames = [f for f in os.listdir(from_path) if not is_special(f)]
    if len(filenames) == 0:
        # TODO: Delete directory if delete_empty
        print('-> No files to move!')
        return

    file_index = random.randint(0, len(filenames) - 1)
    filename = filenames[file_index]

    print('-> From:', from_path)
    print('->   To:', to_path)
    print('-> File:', filename)

    shutil.move(os.path.join(from_path, filename), to_path)


def extract_attribute(name, delimiter, pattern, default=None):
    m = re.search(r'{0}(?P<value>{1})'.format(delimiter, pattern), name)
    if not m:
        return default

    value = m.groupdict()['value']
    if value is None:
        return default

    return value


def move_random_file_ext(from_path, to_path):
    filenames = [f for f in os.listdir(from_path) if is_special(f)]
    if len(filenames) == 0:
        return

    for filename in filenames:
        print()
        print('***', filename, '***')

        attributes = {
            'dayofweek': extract_attribute(filename, r'@', r'[A-Za-z]+'),
            'repeat': int(extract_attribute(filename, r'\+', r'[0-9]+', 1)),
        }
        filename = os.path.join(from_path, filename)

        if attributes['dayofweek']:
            dayofweek = attributes['dayofweek'].lower()
            if dayofweek != WEEKDAYS[datetime.today().weekday()]:
                print('-> Not moving; today is not "{0}"'.format(dayofweek))
                continue

        for i in range(attributes['repeat']):
            move_random_file(filename, to_path)


def run(argv=None):
    if not argv:
        argv = sys.argv
    if len(argv) < 3:
        print('Usage')
        print('  mvrnd <from> <to>')
        return 2
    move_random_file(argv[1], argv[2])
    move_random_file_ext(argv[1], argv[2])
    return 0


if __name__ == '__main__':
    sys.exit(run())
