import os
from uuid import uuid4

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


@pytest.fixture
def folder_path():
    return f"pytest_folder_{uuid4().hex[:12]}"


@pytest.fixture
def existing_folder(disk_client, folder_path):
    response = disk_client.create_folder(folder_path)
    assert response.status_code == 201

    yield folder_path

    disk_client.delete_resource(
        folder_path,
        permanently=True,
    )