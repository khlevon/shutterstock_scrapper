import argparse
import json
from pathlib import Path
from queue import Queue
from threading import Thread
from multiprocessing import cpu_count
from shutterstock_scrapper import ShutterstockDownloader, ShutterstockScrapper, ShutterstockCSVWriter


def main(keywords, credentials, root_dir):
    root_dir.mkdir(exist_ok=True)

    scrapper_queue = Queue()
    downloader_queue = Queue()
    writer_queue = Queue()

    for keyword in keywords:
        scrapper_queue.put(keyword)

    # run ShutterstockScrapper threads
    for credentials in credentials:
        Thread(
            target=ShutterstockScrapper.thread_worker,
            args=(
                scrapper_queue, downloader_queue, credentials
            ),
            daemon=True
        ).start()

    # run ShutterstockDownloader threads
    for _ in range(cpu_count() * 2):
        Thread(
            target=ShutterstockDownloader.thread_worker,
            args=(
                downloader_queue,
                writer_queue,
                {
                    "root_path": root_dir,
                }
            ),
            daemon=True
        ).start()

    # run ShutterstockCSVWriter thread
    Thread(
        target=ShutterstockCSVWriter.thread_worker,
        args=(
            writer_queue,
            {
                "header": [
                    'searched_keyword',
                    'photo_id',
                    'keywords',
                    'description',
                    'category',
                    'file_path',
                ],
                "file_path": root_dir / "metadata.csv"
            }
        ),
        daemon=True
    ).start()

    scrapper_queue.join()
    downloader_queue.join()
    writer_queue.join()


if __name__ == "__main__":

    args = argparse.ArgumentParser(description='Shutterstock Scrapper')
    args.add_argument('-d', '--root_dir', type=str, required=True,
                      help='Path to folder where the images will be downloaded')
    args.add_argument('-k', '--keywords', type=str, required=True,
                      help='Path to file which contains keywords to search for')
    args.add_argument('-c', '--credentials', type=str, required=True,
                      help='Path to json file which contains credentials to use for ShutterstockScrapper')

    parsed_args = args.parse_args()

    # KEYWORDS = [
    # "sad person portrait NOT:vector",
    # "suprise person portrait NOT:vector",
    # "fear person portrait NOT:vector",
    # "disgust person portrait NOT:vector",
    # "anger person portrait NOT:vector",
    # ]
    # CREDENTIALS = [{"username": "B7sQbooBMKdb6DAHiZSqPAdBwQsiVZPL", "password": "FFknwUnSErYwgJrl"}, {"username": "B7sQbooBMKdb6DAHiZSqPAdBwQsiVZPL", "password": "FFknwUnSErYwgJrl"}, {"username": "29nPikK4VnNHKoJGic50A1G4Kndk8xJs", "password": "69O5Hiav23ogdB6y"}, {"username": "zvR1qR8ZPi9GITQ1xTq5ZmUpwE5wXqod", "password": "puaRPm3jGkM2GbOA"}, {"username": "sUMc7ncLw1xXRxhkku9TJniBGsCnGqQZ", "password": "Zs0sLHRnmhr9pSGw"}, {"username": "AUP3cAGbFcgRHmABWbpmI8T220GgUdwe", "password": "jAhaifft9LtUYCXu"}, {"username": "KTGRIbUjeFWRTogvKsqqu0kpmsbWVryL", "password": "vaEHlK8yETKIVgfN"}, {"username": "ut0lGVssmzWyFsUOxKqBHEjkwxqYK1ar", "password": "nEqlhnNAJ9kotDVD"}, {"username": "Pm4zQRQhxWyVjPzT9xCMdSA7JrFG9eP9", "password": "QodzjK0hfgEymAjr"}, {"username": "PGFC52ObIc75ygGZ5JNNZL5SAYtkYiFd", "password": "2UNgsTyNVMXBOZ5N"}, {"username": "Y4qqeff6qS28dk31ASifCAd499EG1R7n", "password": "H5FSpwQpJ8Vfr1l4"}, {"username": "OkSFL2QNgAAbs7AlAsZkWUzqfGzEcRjY", "password": "crBNgmzJYMA7P5v3"}, {"username": "ehXS6RdKI0RepgUGRKz5W4KXH75Wa3za", "password": "LRU7nAi0DZmco4UL"}, {"username": "kTNKGvB6DA0eqF76blVIVaW3YYpBmt1M", "password": "atkJktjqJlBEAK48"}, {"username": "HdFlIMvCenMkqDGG0fnkv8tGbcInbzot", "password": "FkB7mBJ6yqfm2qfs"}, {"username": "nzclIeqV6xIa9K2z8vAkLKcpyHCqJY9T", "password": "55oFVKAV5Yg8mwVX"}, {"username": "BOlGFXzNdcjBjpyElk9NQUtj2mzM34xA", "password": "lola8BBfGxhc8G5I"}, {"username": "VDAeLgRTZG7yxhP4ZmVHHmgJKeGLkscA", "password": "oreejO8jxvwo4mEM"}, {"username": "1qmbIRgfK93xL1q563qhY6xoDky2NWHr", "password": "bmme2mH7RIpA9xxY"}, {"username": "FAxIoHq4zxWSQYm7lF8MsorddJ3UUp2e", "password": "du7MdvMawerRgzOa"}, {"username": "J2GvppmjBZGEPPHAvXH6g4gvjV4bmBk5", "password": "JrO4K3BH9zSdvodX"}]

    keywords = open(parsed_args.keywords,
                    "r").read().splitlines(keepends=False)
    credentials = json.loads(open(parsed_args.credentials, "r").read())
    root_dir = Path(parsed_args.root_dir)

    print("Start scrapping")

    main(keywords, credentials, root_dir)

    print("Done!!!")
