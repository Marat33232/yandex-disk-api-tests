from uuid import uuid4

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