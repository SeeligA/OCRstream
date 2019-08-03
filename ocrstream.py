
import logging
from time import sleep
from multiprocessing.pool import Pool

from sources.transform import find_failed_conversions, flat_convert, run_ocr, terminate_finereader
from sources.extract import extract_source_files
from sources.load import load_to_corpus

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class MyPipeline(object):

    def __init__(self):
        self.TIMEOUT = 60
        self.SLEEP = 10
        self.BATCH_SIZE = 50
        self.cache = dict()

    def extract_files(self):
        """
        Copy project source files listed in TW export to target directory (TOP DIR)

        Arguments:
             fp -- path to TW CSV export with the following columns:
                    addressID, auftragsDatum, projektNR, D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID
        """

        self.cache = extract_source_files()

    @staticmethod
    def convert():
        """Fetch extracted files and convert them to TXT files.

        The method uses the PowerGrep converter out of the box. It is a "flat" conversion, because it normalizes
        the path to CLIENT/PROJECT-ID/FILENAME
        """
        flat_convert()

    def ocr(self):

        fails = find_failed_conversions()

        def batch(my_list, n=1):
            """Slice a list of strings into n-sized batches"""
            length = len(my_list)
            for ndx in range(0, length, n):
                yield my_list[ndx:min(ndx + n, length)]

        for x in batch(fails, self.BATCH_SIZE):
            self.batch_workers(x)

        logging.info("No. of empty files: {}.".format(len(find_failed_conversions())))

    def batch_workers(self, fails):

        pool = Pool(processes=len(fails))

        # Spawn a new worker for each doc that requires OCR processing
        # The number of concurrently running workers is determined by the number of CPU cores
        for i in range(len(fails)):
            pool.apply_async(run_ocr, args=(fails[i], self.cache))
            # Add sleep time to prevent licensing errors messages
            sleep(self.SLEEP)

        pool.close()
        print("Waiting for FineReader to finish…", end='')

        cnt = 0
        while len(find_failed_conversions()) > 0 and cnt < self.TIMEOUT:
            print(".", end='')
            sleep(self.SLEEP)
            cnt += self.SLEEP

        terminate_finereader()
        pool.join()
        logging.info("All processes joined")

    def load(self):
        load_to_corpus(self.cache)


if __name__ == '__main__':
    p = MyPipeline()
    p.extract_files()
    p.convert()
    p.ocr()
    p.load()
