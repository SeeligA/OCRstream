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


def delete_dir(directory):
    """Delete local working folder.

    Arguments:
        directory -- Path to local folder as string.
    """
    # IMPORTANT: This condition prevents you from accidentally deleting data on a network mount:
    drive = 'C:'
    if os.path.splitdrive(directory)[0] != drive:
        raise Exception(f'Unable to remove {directory}. Check if path is valid and on drive {drive}.')

    elif os.path.exists(directory):
        shutil.rmtree(directory)
        logging.info(f'{directory} has been removed')
    else:
        pass
