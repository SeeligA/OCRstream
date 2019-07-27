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
    # Copy source files to target path
    if os.path.exists(src):
        if not os.path.exists(dst):
            os.makedirs(dst, exist_ok=True)

        shutil.copy(src, dst)
        logging.info('Copying files to: {}'.format(dst))

    else:
        logging.info('Skipped file {}. Path does not exist.'.format(src))
