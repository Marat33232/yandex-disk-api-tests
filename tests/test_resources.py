from uuid import uuid4
import time
import requests


def assert_error_response(response):
    data = response.json()

    assert "error" in data
    assert "message" in data


def test_create_folder(disk_client, folder_path):
    try:
        response = disk_client.create_folder(folder_path)
        assert response.status_code == 201

        get_response = disk_client.get_resource(folder_path)
        assert get_response.status_code == 200

        data = get_response.json()

        assert data["name"] == folder_path
        assert data["type"] == "dir"
        assert data["path"] == f"disk:/{folder_path}"

    finally:
        disk_client.delete_resource(
            folder_path,
            permanently=True,
        )


def test_create_folder_without_path(disk_client):
    response = disk_client.create_folder()

    assert response.status_code == 400
    assert_error_response(response)


def test_create_existing_folder(disk_client, existing_folder):
    response = disk_client.create_folder(existing_folder)

    assert response.status_code == 409
    assert_error_response(response)

    get_response = disk_client.get_resource(existing_folder)
    assert get_response.status_code == 200


def test_get_existing_folder(disk_client, existing_folder):
    response = disk_client.get_resource(existing_folder)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == existing_folder
    assert data["type"] == "dir"
    assert data["path"] == f"disk:/{existing_folder}"


def test_get_resource_with_fields(disk_client, existing_folder):
    response = disk_client.get_resource(
        existing_folder,
        fields="name,type,path",
    )

    assert response.status_code == 200

    data = response.json()

    assert "name" in data
    assert "type" in data
    assert "path" in data

    assert data["name"] == existing_folder
    assert data["type"] == "dir"


def test_get_resource_without_path(disk_client):
    response = disk_client.get_resource()

    assert response.status_code == 400
    assert_error_response(response)


def test_get_nonexistent_resource(disk_client):
    path = f"missing_{uuid4().hex}"

    response = disk_client.get_resource(path)

    assert response.status_code == 404
    assert_error_response(response)


def test_get_resource_without_auth(existing_folder, disk_client):
    response = requests.get(
        f"{disk_client.BASE_URL}/resources",
        params={"path": existing_folder},
        timeout=10,
    )

    assert response.status_code == 401
    assert_error_response(response)


def wait_for_operation(disk_client, href, timeout=15, interval=0.5):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        response = disk_client.get_operation(href)
        assert response.status_code == 200

        data = response.json()
        status = data["status"]

        if status == "success":
            return data

        if status == "failed":
            raise AssertionError(
                f"Async operation failed: {data}"
            )

        time.sleep(interval)

    raise AssertionError(
        f"Async operation did not finish within {timeout} seconds"
    )


def wait_if_async(disk_client, response):
    if response.status_code == 202:
        data = response.json()

        assert "href" in data

        wait_for_operation(
            disk_client,
            data["href"],
        )


def test_copy_folder(disk_client, existing_folder):
    destination = f"copy_{uuid4().hex[:12]}"

    try:
        response = disk_client.copy_resource(
            existing_folder,
            destination,
        )

        assert response.status_code in (201, 202)

        wait_if_async(disk_client, response)

        get_response = disk_client.get_resource(destination)
        assert get_response.status_code == 200

        data = get_response.json()

        assert data["name"] == destination
        assert data["type"] == "dir"

    finally:
        disk_client.delete_resource(
            destination,
            permanently=True,
        )


def test_copy_nonexistent_resource(disk_client):
    source = f"missing_{uuid4().hex}"
    destination = f"copy_{uuid4().hex}"

    response = disk_client.copy_resource(
        source,
        destination,
    )

    assert response.status_code == 404
    assert_error_response(response)


def test_copy_to_existing_destination(
    disk_client,
    existing_folder,
):
    destination = f"existing_copy_{uuid4().hex[:12]}"

    create_response = disk_client.create_folder(destination)
    assert create_response.status_code == 201

    try:
        response = disk_client.copy_resource(
            existing_folder,
            destination,
        )

        assert response.status_code == 409
        assert_error_response(response)

    finally:
        disk_client.delete_resource(
            destination,
            permanently=True,
        )


def test_copy_force_async(disk_client, existing_folder):
    destination = f"async_copy_{uuid4().hex[:12]}"

    try:
        response = disk_client.copy_resource(
            existing_folder,
            destination,
            force_async=True,
        )

        assert response.status_code == 202

        data = response.json()
        assert "href" in data

        wait_for_operation(
            disk_client,
            data["href"],
        )

        get_response = disk_client.get_resource(destination)
        assert get_response.status_code == 200

    finally:
        disk_client.delete_resource(
            destination,
            permanently=True,
        )


def test_delete_resource_permanently(
    disk_client,
    existing_folder,
):
    response = disk_client.delete_resource(
        existing_folder,
        permanently=True,
    )

    assert response.status_code in (202, 204)

    wait_if_async(disk_client, response)

    get_response = disk_client.get_resource(existing_folder)

    assert get_response.status_code == 404


def test_delete_nonexistent_resource(disk_client):
    path = f"missing_{uuid4().hex}"

    response = disk_client.delete_resource(
        path,
        permanently=True,
    )

    assert response.status_code == 404
    assert_error_response(response)