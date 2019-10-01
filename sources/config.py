import os

BASE_DIR = os.getcwd()

#  TODO: Replace paths to match your folder structure
# Specify local working directory.
TOP_DIR = "C:\\Users\\seelig\\01pdf_temp"
# Specify local staging directory containing the TXT training files
CORPUS_TEMP = "C:\\Users\\seelig\\02corpus_temp\\"

# Path to project file containing client IDs, project IDs and language IDs
PROJECT_DATABASE_EXPORT = os.path.join("data", "_SAMPLE_DATA\\order_out.csv")
# Path to source files
source_root = 'F:\\ORDER_DIRECTORY'

# Specify paths to application folders containing executables.
# Paths will be used in the commandline. No need to normalize them.
PATH_TO_PG = "C:\Program Files\Just Great Software\PowerGREP 5"
PATH_TO_FR = "C:\Program Files (x86)\ABBYY FineReader 11"
# Path to PowerGrep action specification XML
PATH_TO_PGA = "sources\\flat_conversion_to_txt_(all_formats).pga"
# Set threshold of what is considered a failed PDF-to-TXT conversion (in bytes)
FILE_SIZE_FILTER = 200

#  TODO: Replace dictionaries to match your OCR needs
# Specify clients to be considered when fetching the source files
# The key relates to the client ID used in PROJECT_DATABASE_EXPORT
# The value relates to the name of the client directory under source_root.
clients_dict = {"4": "Fine Apples Ltd. 4",
                "2774": "Foo Business Associates 2774",
                "1552": "Hengel, Hengel & Hengeler 1552",
                "20522": "Rob Cole Medical Solutions GmbH 20522"
                }

# Map strings to languages used for OCR processing.
# Keys relate to the language specifier used in PROJECT_DATABASE_EXPORT.
# Other languages have been added to account for multilingual content.
lid_dict = {"01": "english french german italian",
            "02": "english french german italian",
            "03": "english french german italian",
            "04": "english french german spanish",
            "05": "english french german italian",
            "06": "english german danish",
            "07": "english german swedish",
            "08": "english german finnish",
            "09": "english german norwegian",
            "10": "english french german dutch",
            "11": "english german PortugueseBrazilian PortugueseStandard",
            "12": "english german SerbianLatin SerbianCyrillic",
            "13": "english german croatian",
            "14": "english german turkish",
            "15": "english german greek",
            "16": "english german russian",
            "17": "english german bulgarian",
            "18": "english german hungarian",
            "19": "english german polish",
            "20": "english german czech",
            "21": "english german romanian",
            "22": "english german japanese",
            "23": "english german chinese",
            "24": "english german arabic",
            "25": "english german SerbianLatin SerbianCyrillic",
            "26": "english german estonian",
            "27": "english german hebrew",
            "28": "english german korean",
            "30": "english german slovenian",
            }
