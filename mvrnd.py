from __future__ import print_function, unicode_literals

import codecs
import errno
import os
import random
import re
import shutil
import sys
from traceback import print_exc
from datetime import datetime


try:
    input = raw_input
except NameError:
    pass


ENCODING = sys.stdout.encoding or 'utf-8'
WEEKDAYS = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']


codecs.register_error('dash', lambda e: (u'-', e.start + 1))


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

    print('-> From:', from_path.encode(ENCODING, 'dash'))
    print('->   To:', to_path.encode(ENCODING, 'dash'))
    print('-> File:', filename.encode(ENCODING, 'dash'))

    try:
        os.makedirs(to_path)
    except OSError as ex:
        if ex.errno != errno.EEXIST or not os.path.isdir(to_path):
            raise

    shutil.move(os.path.join(from_path, filename), to_path)


def move_random_files(from_path, to_path):
    # Move random non-special files and subdirectories
    move_random_file(from_path, to_path)

    # Recurse through special directories
    for filename in os.listdir(from_path):
        if not is_special(filename):
            continue

        print()
        print('***', filename.encode(ENCODING, 'dash'), '***')
        next_from_path = os.path.join(from_path, filename)
        next_to_path = os.path.join(to_path, filename)

        # Filter day-of-week
        dayofweek = _extract_attribute(next_from_path, r'@', r'[A-Za-z]+')
        if dayofweek:
            if dayofweek.lower() != WEEKDAYS[datetime.today().weekday()]:
                print('-> Not moving; today is not "{0}"'.format(dayofweek))
                continue

        # Repeated recursions
        count = _extract_attribute(next_from_path, r'\+', r'[0-9]+')
        if count:
            repeat = int(count) - 1
            for i in range(repeat):
                move_random_file(next_from_path, next_to_path)

        # Recurse
        move_random_files(next_from_path, next_to_path)


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

    try:
        move_random_files(argv[1].decode(ENCODING), argv[2].decode(ENCODING))
        return 0
    except Exception:
        print_exc()
        input('Press ENTER to continue . . .')
        return 1


if __name__ == '__main__':
    sys.exit(run())
