from pathlib import Path
from queue import Queue
from PIL import Image
import io
import requests
import tempfile


class ShutterstockDownloader:
    def __init__(self, root_path: Path) -> None:
        self._root_path = root_path

    def _download_image(self, img_url: str) -> Image:
        # save file on disk if size is larger then 10MB
        buffer = tempfile.SpooledTemporaryFile(max_size=1024 * 1024 * 10)
        try:
            r = requests.get(img_url, stream=True)
            if r.status_code == 200:
                # downloaded = 0
                # file_size = int(r.headers['content-length'])
                # set download chunk size 20KB
                for chunk in r.iter_content(chunk_size=1024 * 20):
                    # downloaded += len(chunk)
                    buffer.write(chunk)
                    # print(int((downloaded / file_size) * 100), "%")
                buffer.seek(0)
            else:
                raise Exception(
                    f"Failed download: \n img_url={img_url} \n status_code={r.status_code}"
                )
        except Exception as e:
            raise e
        else:
            img = Image.open(io.BytesIO(buffer.read()))
            return img
        finally:
            buffer.close()

    def _process_image(self, img: Image) -> Image:
        # cropping, resizing and converting back to an image
        width, height = img.size

        new_height = (height / 100) * 93

        box = (0, 0, width, new_height)
        img = img.crop(box)

        return img

    def _save_image(self, img_binary: bytes, name: str) -> Path:
        # save file on disk
        file_path = self._root_path / name
        with open(file_path, "wb+") as f:
            f.write(img_binary)

        return file_path

    def process_metadata(self, metadata: dict):
        searched_keyword = metadata["searched_keyword"]
        photo_id = metadata["photo_id"]
        image_url = metadata["thumb"]["url"]

        img = self._download_image(image_url)
        img = self._process_image(img)

        in_mem_file = io.BytesIO()
        img.save(in_mem_file, format="JPEG", optimize=False, quality=100)

        file_path = self._save_image(
            in_mem_file.getvalue(),
            f"{searched_keyword.split(' ')[0]}_{photo_id}.jpeg"
        )

        return {
            'searched_keyword': searched_keyword,
            'photo_id': photo_id,
            'keywords': metadata["keywords"],
            'description': metadata["description"],
            'category': metadata["category"],
            'file_path': file_path
        }

    def thread_worker(task_queue: Queue, result_queue: Queue, config: dict):
        downloader = ShutterstockDownloader(**config)
        while True:
            task = task_queue.get()
            if task is None:
                break

            try:
                result = downloader.process_metadata(task)
                result_queue.put(result)
            except Exception as e:

                # print("Failed to process metadata for: ", task, e)
                continue
            finally:
                task_queue.task_done()
