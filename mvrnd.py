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
    prompt = raw_input
except NameError:
    prompt = input


DAY_NAMES = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']
WORKDAY_NAMES = ['mon', 'tues', 'wed', 'thurs', 'fri']
WORKDAY = 'work'
MONTHLY = 'monthly'
YEARLY = 'yearly'


codecs.register_error('dash', lambda e: (u'-', e.start + 1))


def is_group(filename):
    return filename.startswith('{') and filename.endswith('}')


def is_recursive(filename):
    return filename.startswith('(') and filename.endswith(')')


def is_recursive_copy(filename):
    return filename.startswith('([') and filename.endswith('])')


def move_random_file(from_dir, to_dir, collect=None, in_group=False):
    if not in_group:
        print('Moving a random file...')

    # Collect all non-recursive files and do nothing if this set is empty
    filenames = [f for f in os.listdir(from_dir) if not is_recursive(f)]
    if collect:
        collected_here = collect.get(from_dir, [])
        filenames = [f for f in filenames if f not in collected_here]
    if len(filenames) == 0:
        print('-> No files to move!')
        return False

    # Pick a file at random
    file_index = random.randint(0, len(filenames) - 1)
    filename = filenames[file_index]
    from_path = os.path.join(from_dir, filename)
    to_path = os.path.join(to_dir, filename)

    # If file is a non-empty group, pick a random file out of the group
    if is_group(filename):
        moved = move_random_file(from_path, to_path, collect, True)
        # Clean up empty groups
        if not os.listdir(from_path):
            try:
                os.rmdir(from_path)
            except OSError as ex:
                # Ignore "not empty" errors, raise all others
                if ex.errno != errno.ENOTEMPTY:
                    raise
        return moved

    print('-> From:', from_path)
    print('->   To:', to_dir)

    # Do nothing if dry-run
    if collect is not None:
        collect.setdefault(from_dir, []).append(filename)
        return True

    # Create target directory (if it doesn't exist)
    try:
        os.makedirs(to_dir)
    except OSError as ex:
        if ex.errno != errno.EEXIST or not os.path.isdir(to_dir):
            raise

    # Move the file
    shutil.move(from_path, to_dir)
    return True


def move_random_files(from_dir, to_dir, count=None, collect=None):
    # Move up to N random non-special files and subdirectories
    for i in range(count or 1):
        if not move_random_file(from_dir, to_dir, collect):
            break

    # Recurse through special directories
    for filename in os.listdir(from_dir):
        if not is_recursive(filename):
            continue

        print()
        print('***', filename, '***')

        # Compute next subdirectories
        next_from_dir = os.path.join(from_dir, filename)
        next_to_dir = (os.path.join(to_dir, filename) if
                       is_recursive_copy(filename) else
                       to_dir)

        # Filter day-of-week
        day_raw = _extract_attribute(next_from_dir, r'@', r'[A-Za-z]+')
        if day_raw:
            day = day_raw.lower()
            today = datetime.today()
            today_name = DAY_NAMES[today.weekday()]
            if day in DAY_NAMES and day != today_name:
                print('-> Not moving; today is not "{0}"'.format(day_raw))
                continue
            if day == MONTHLY and today.day != 1:
                print('-> Not moving; today is not the first of the month')
                continue
            if day == YEARLY and (today.day != 1 or today.month != 1):
                print('-> Not moving; today is not the first of the year')
                continue
            if day == WORKDAY and today_name not in WORKDAY_NAMES:
                print('-> Not moving; today is not a work day')
                continue

        # Repeated recursions
        next_count = _extract_attribute(next_from_dir, r'\+', r'[0-9]+')
        if next_count:
            next_count = int(next_count)

        # Recurse
        move_random_files(next_from_dir, next_to_dir, next_count, collect)


def _extract_attribute(name, delimiter, pattern):
    m = re.search(r'{0}(?P<value>{1})'.format(delimiter, pattern), name)
    return m.groupdict()['value'] if m else None


def run(argv=None):
    if not argv:
        argv = sys.argv

    dry_run = False
    if '--dry-run' in argv:
        argv.remove('--dry-run')
        dry_run = True
    if '-d' in argv:
        argv.remove('-d')
        dry_run = True

    if len(argv) < 3:
        print('Usage')
        print('  mvrnd <from> <to>')
        return 2

    try:
        move_random_files(argv[1], argv[2], collect=({} if dry_run else None))
        return 0
    except Exception:
        print_exc()
        prompt('Press ENTER to continue . . .')
        return 1


if __name__ == '__main__':
    sys.exit(run())
