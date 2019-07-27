import os
import shutil
import csv
import logging

from sources.utils import copy_dirs

TOP_DIR = "C:\\Users\\seelig\\extract"


def copy_source_files(fp, source_root):

    # Clear target directory if it already exists.
    # The second condition prevents you from accidentally deleting paths on F: or O:
    if os.path.exists(TOP_DIR) and os.path.splitdrive(TOP_DIR)[0] == 'C:':
        shutil.rmtree(TOP_DIR)
        logging.info('{} has been removed'.format(TOP_DIR))

    # Process projects entries in CSV line per line
    with open(fp, newline='') as csvfile:
        datareader = csv.DictReader(csvfile, delimiter=';', quotechar='|')
        for row in datareader:

            #if row['adressID'] == "11385":
            source_dir = '{}-{}\\01_Orig'.format(row['projektNr'], row['adressID'])
            target_dir = '{}\\{}-{}'.format(row['D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID'][:-2], row['projektNr'],
                                            row['adressID'])
            src = os.path.join(source_root, source_dir)
            dst = os.path.join(TOP_DIR, target_dir)

            copy_dirs(src, dst)
