import os
import shutil
import csv
import logging

from sources.utils import copy_dirs

TOP_DIR = "C:\\Users\\seelig\\pdf_ocr"


def copy_source_files(fp, client_dict, source_root):
    """
    Copy project source files listed in TW export to target directory (TOP DIR)

    Arguments:
        fp -- path to TW CSV export with the following columns:
                addressID, auftragsDatum, projektNR, D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID

        client_dict -- Dictionary mapping addressIDs to names used in the folder directory
        source_root -- base path to project directories (either on f: or on o:)

    Returns:

        cache -- Dictionary mapping project folder names to source language ids
    """

    # Clear target directory if it already exists.
    # The second condition prevents you from accidentally deleting paths on F: or O:
    if os.path.exists(TOP_DIR) and os.path.splitdrive(TOP_DIR)[0] == 'C:':
        shutil.rmtree(TOP_DIR)
        logging.info('{} has been removed'.format(TOP_DIR))

    # Process projects entries in CSV line per line
    with open(fp, newline='') as csvfile:
        datareader = csv.DictReader(csvfile, delimiter=';', quotechar='|')
        cache = dict()
        for row in datareader:

            # Check addressID value against keys in client dictionary
            client = client_dict.get(row['adressID'], None)
            if client:

                # Build paths for source and target directories from TW data
                # Example Source: F:\Kundenaufträge ab Dez 2010\CLIENT 123456\03_Projekte\XXXXXX-123456\01_Orig
                # Example Target: C:\Users\seelig\extract\CLIENT 123456\XXXXXX-123456
                project_folder = '{}-{}'.format(row['projektNr'], row['adressID'])

                # Note: This hack is only suitable for Windows. Use os.path.join() or pathlib for proper path handling.
                source_dir = '{}\\{}\\{}\\01_Orig'.format(client, "03_Projekte", project_folder)
                target_dir = '{}\\{}'.format(client, project_folder)

                src = os.path.join(source_root, source_dir)
                dst = os.path.join(TOP_DIR, target_dir)

                # Call utility function to copy 01_Orig files to target path
                copy_dirs(src, dst)

                # We store the source language ID to use it as a parameter in the retrieve_lid call during ocr
                cache[project_folder] = [client, row['D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID'][:-2]]

    return cache
