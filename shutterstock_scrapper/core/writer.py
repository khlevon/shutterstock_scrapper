from queue import Queue
import csv


class ShutterstockCSVWriter:
    def thread_worker(task_queue: Queue, config: dict):
        header = config["header"]
        file_path = config["file_path"]
        with open(file_path, "w+") as df:
            csv_writer = csv.writer(df)
            csv_writer.writerow(header)

            while True:
                task = task_queue.get()
                if task is None:
                    break

                try:
                    row = [task.get(key, "") for key in header]
                    csv_writer.writerow(row)
                except Exception as e:

                    # print("Failed to save metadata for: ", task, e)
                    continue
                finally:
                    task_queue.task_done()
