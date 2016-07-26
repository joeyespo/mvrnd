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


def move_random_file(from_path, to_path):
    print('Moving a random file...')

    filenames = [f for f in os.listdir(from_path) if not is_special(f)]
    if len(filenames) == 0:
        print('-> No files to move!')
        return

    file_index = random.randint(0, len(filenames) - 1)
    filename = filenames[file_index]

    print('-> From:', from_path)
    print('->   To:', to_path)
    print('-> File:', filename)

    os.makedirs(to_path)
    shutil.move(os.path.join(from_path, filename), to_path)


def move_random_files(from_path, to_path):
    # Move random non-special files and subdirectories
    move_random_file(from_path, to_path)

    # Recurse through special directories
    for filename in os.listdir(from_path):
        if not is_special(filename):
            continue

        print()
        print('***', filename, '***')
        current_path = os.path.join(from_path, filename)
        next_path = os.path.join(to_path, filename)

        # Filter day-of-week
        dayofweek = _extract_attribute(current_path, r'@', r'[A-Za-z]+')
        if dayofweek:
            if dayofweek.lower() != WEEKDAYS[datetime.today().weekday()]:
                print('-> Not moving; today is not "{0}"'.format(dayofweek))
                continue

        # Repeated recursions
        count = _extract_attribute(current_path, r'\+', r'[0-9]+')
        if count:
            repeat = int(count) - 1
            for i in range(repeat):
                move_random_file(current_path, next_path)

        # Recurse
        move_random_files(current_path, next_path)


def _extract_attribute(name, delimiter, pattern):
    m = re.search(r'{0}(?P<value>{1})'.format(delimiter, pattern), name)
    return m.groupdict()['value'] if m else None


def run(argv=None):
    if not argv:
        argv = sys.argv
    if len(argv) < 3:
        print('Usage')
        print('  mvrnd <from> <to>')
        return 2

    move_random_files(argv[1], argv[2])
    return 0


if __name__ == '__main__':
    sys.exit(run())
