import os
import pytest
from dotenv import load_dotenv
from api.disk_client import YandexDiskClient

load_dotenv()


@pytest.fixture(scope="session")
def disk_client():

    token = os.getenv("YANDEX_DISK_TOKEN")


    if not token:
        pytest.fail("YANDEX_DISK_TOKEN is not set in .env")

    return YandexDiskClient(token)