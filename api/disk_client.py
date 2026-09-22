import requests


class YandexDiskClient:
    BASE_URL = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"OAuth {token}"
        })

    def create_folder(self, path):
        return self.session.put(
            f"{self.BASE_URL}/resources",
            params={"path": path},
            timeout=10,
        )

    def get_resource(self, path, fields=None):
        params = {"path": path}

        if fields:
            params["fields"] = fields

        return self.session.get(
            f"{self.BASE_URL}/resources",
            params=params,
            timeout=10,
        )

    def copy_resource(self, source, destination, overwrite=False, force_async=False):
        return self.session.post(
            f"{self.BASE_URL}/resources/copy",
            params={
                "from": source,
                "path": destination,
                "overwrite": overwrite,
                "force_async": force_async,
            },
            timeout=10,
        )

    def delete_resource(self, path, permanently=False, force_async=False):
        return self.session.delete(
            f"{self.BASE_URL}/resources",
            params={
                "path": path,
                "permanently": permanently,
                "force_async": force_async,
            },
            timeout=10,
        )