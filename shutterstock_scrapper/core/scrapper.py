from queue import Queue
from typing import List
from shutterstock_sdk import Configuration, ImagesApi, ApiClient
from shutterstock_sdk.rest import ApiException
import time
import json


class ShutterstockScrapper:
    api: ImagesApi

    def __init__(self, username, password):

        configuration = Configuration()
        configuration.username = username
        configuration.password = password
        self.api = ImagesApi(ApiClient(configuration))

    def fetch_metadata_by_keyword(self, keyword: str) -> List[dict]:
        result: List[dict] = []
        page = 1
        failovers = 0

        while True:
            try:
                response = self.api.search_images(
                    view='full',
                    language='en',
                    per_page=25,
                    page=page,
                    query=keyword,
                )
                for item in response.data:
                    result.append({
                        'searched_keyword': keyword,
                        'keywords': list(item.keywords),
                        'photo_id': item.id,
                        'description': item.description,
                        'category': list(map(lambda i: {"id": i.id, "name": i.name}, item.categories)),
                        'thumb': {
                            'width': item.assets.huge_thumb.width,
                            'height': item.assets.huge_thumb.height,
                            'url': item.assets.huge_thumb.url
                        }
                    })

                if len(response.data) < 25:  # if it is last page break loop
                    break

                page += 1
                failovers = 0

            except ApiException as e:
                if e.status == 429:
                    body = json.loads(e.body)
                    current_time = int(time.time() * 1000)
                    reset_time = body.get("reset", int(
                        (time.time() + 60 * 60) * 1000))
                    wait_milliseconds = (
                        reset_time - current_time) + (60 * 1000)  # add 60 seconds
                    time.sleep(wait_milliseconds * 1000)
                else:
                    failovers += 1
                    if failovers > 3:
                        # print("Failed to fetch metadata for keyword: " + keyword)
                        # print("Error: ", e)
                        break
                    time.sleep(10)

        return result

    def thread_worker(task_queue: Queue, result_queue: Queue, config: dict):
        scrapper = ShutterstockScrapper(**config)
        while True:
            task = task_queue.get()
            if task is None:
                break

            try:
                result = scrapper.fetch_metadata_by_keyword(task)
                for item in result:
                    result_queue.put(item)
            except Exception as e:
                # print("Failed to fetch metadata for keyword: ", task, e)
                continue
            finally:
                task_queue.task_done()
