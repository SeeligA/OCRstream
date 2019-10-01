import os
from collections import Counter, defaultdict

import pandas as pd

from sources.utils import copy_files, delete_dir
from sources.config import TOP_DIR, CORPUS_TEMP, DATABASE_EXPORTS_FOLDER


def load_to_corpus(cache):


    delete_dir(CORPUS_TEMP)

    for root, dirs, files in os.walk(TOP_DIR):
        for file in filter(lambda file: file.lower().endswith('.txt'), files):

            src = os.path.join(root, file)
            # Extract project folder from path
            project_folder = os.path.basename(root)
            # Lookup client folder in cache dictionary
            client_folder = cache.get(project_folder, 'Fail')[0]

            dst = os.path.join(CORPUS_TEMP, os.path.join(client_folder, project_folder))

            copy_files(src, dst)


def get_most_recent_folder():
    """Get most recent folder in data folder."""
    root = DATABASE_EXPORTS_FOLDER
    all_subdirs = [os.path.join(root, d) for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    return latest_subdir


def get_most_recent_export(latest_subdir):
    for file in filter(lambda file: file.lower().endswith(('.csv', '.xlsx')), os.listdir(latest_subdir)):
        if file == "order_out.csv":
            raise Exception(f'Process skipped. File {file} already exists!')

    return file


def load_data(fp):
    try:

        df = pd.read_excel(fp, na_values='eco',  # Unsure why "eco" is in the spp column, only numerics are allowed
                           dtype={"adressID": str,
                                  "auftragsDatum": str,
                                  "projektNr": str,
                                  "D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID": str}
                           )
        df.dropna(subset=["D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID"], inplace=True)

        df.fillna(method='ffill', inplace=True)

    except ValueError:
        print(f'{fp}')

    return df


def count_spps(df):
    """Get most probable source language per project."""
    prj_to_spp = defaultdict(str)

    # Iterate over unique project ids
    for prj in df['projektNr'].unique():
        # Extract source language id from strings in spp column.
        spps = df[df['projektNr'] == prj]['D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID'].str[0:2].values
        # Iterate over list of strings and count occurrences
        cnt = Counter(spps)
        # If source language id include '00', set count to zero
        if cnt.get('00', False):
            cnt['00'] = 0

        # Map most common source language to project ID
        prj_to_spp[prj] = cnt.most_common(1)[0][0]
    return prj_to_spp


def clean_data(df, prj_to_spp):
    # Replace SPP column with project ID column
    df['D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID'] = df['projektNr']
    # Look up project ID in dictionary and replace table value with dictionary value
    df['D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID'].replace(to_replace=prj_to_spp, inplace=True)
    # Remove rows with duplicate project IDs and return table
    df.drop_duplicates(subset="projektNr", inplace=True)
    return df


def parse_order_data():
    """Pre-process nested order data from ERP export."""
    directory = get_most_recent_folder()

    try:
        src = get_most_recent_export(directory)
    except Exception:
        return os.path.join(directory, "order_out.csv")

    df = load_data(os.path.join(directory, src))
    print(f'Loading from to {os.path.join(directory, src)}')

    prj_to_spp = count_spps(df)
    df = clean_data(df, prj_to_spp)
    dst = os.path.join(directory, "order_out.csv")
    df.to_csv(dst, sep=',')
    print(f'Saved to {dst}')
    return dst
