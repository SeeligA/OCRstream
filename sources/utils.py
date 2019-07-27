import shutil
import logging
import os


def copy_dirs(src, dst):
    # Copy source directory recursively to target path
    try:
        dirs = shutil.copytree(src, dst)
        logging.info('Copying files to: {}'.format(dirs))

    except FileNotFoundError:
        logging.info('An error occurred with {}'.format(src))


def copy_files(src, dst):
    # Copy source directory recursively to target path
    if not os.path.exists(dst):
        os.mkdir(dst)

    try:
        shutil.copy(src, dst)
        logging.info('Copying files to: {}'.format(dst))

    except FileNotFoundError:
        logging.info('An error occurred with {}'.format(src))
