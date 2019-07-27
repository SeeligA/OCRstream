import os
import logging

BASE_DIR = os.getcwd()
TOP_DIR = "C:\\Users\\seelig\\extract"
FILE_SIZE_FILTER = 200
PATH_TO_PG = "C:\Program Files\Just Great Software\PowerGREP 5"
PATH_TO_FR = "C:\Program Files (x86)\ABBYY FineReader 11"


def flat_convert(path_to_action):
    """

    path_to_action:

    """
    path_to_exe = PATH_TO_PG
    path_to_results = os.path.join(TOP_DIR, "results.html")

    command = "PowerGrep5.exe /folderrecurse \"" + \
              TOP_DIR + "\" \"" + \
              path_to_action + "\" /silent /save \"" + \
              path_to_results + "\" /quit"

    os.chdir(path_to_exe)
    os.system(command)
    logging.info("Results written to: {}".format(path_to_results))

    os.chdir(BASE_DIR)


def find_failed_conversions():
    """Search for files where conversion has likely failed."""

    fails = []

    for root, dirs, files in os.walk(TOP_DIR):

        for file in filter(lambda file: file.lower().endswith('pdf.txt'), files):
            if os.path.getsize(os.path.join(root, file)) < FILE_SIZE_FILTER:
                fails.append(os.path.join(root, file))
                # yield(os.path.join(root, file))
    return fails


def run_ocr(fp):
    """Run OCR tool on documents that were presumably scanned.
    Arguments:
        fp -- Path to *.txt file flagged because file size < FILE_SIZE_FILTER

    Collects language settings from file path
    """
    lang = retrieve_lid(fp)
    # Remove ".txt" extension from file path
    path_to_file = fp[:-4]

    command = "FineCmd.exe \"" + \
               path_to_file + "\"" + \
               " /lang " + lang + \
               " /out \"" + fp + "\" /quit"

    path_to_exe = PATH_TO_FR
    os.chdir(path_to_exe)

    os.system(command)
    logging.info("OCR results written to: {}".format(fp))
    os.chdir(BASE_DIR)


def terminate_finereader():
    command = "taskkill /T /F /IM FineReader.exe"
    os.system(command)


def retrieve_lid(fp):
    """Parse language ID from path to file."""
    tail = fp[len(TOP_DIR) + 1:]
    lid = os.path.dirname(tail)[0]

    # See "ABBYY FineReader 11/FinereaderCmd.txt" for valid language names
    lid_dict = {"1": "english french german italian",
                "2": "english french german italian",
                "3": "english french german italian",
                "4": "english french german spanish",
                "5": "english french german italian",
                "7": "english french german swedish",
                "10": "english french german dutch",
                "11": "english french german portuguese",
                "13": "english french german croatian",
                "14": "english french german turkish",
                "15": "english french german greek",
                "18": "english french german hungarian",
                "19": "english french german polish",
                "20": "english french german czech",
                "22": "english french german japanese",
                "23": "english french german chinese",
                "27": "english french german hebrew",
                }

    return lid_dict.get(lid, "english french german italian")