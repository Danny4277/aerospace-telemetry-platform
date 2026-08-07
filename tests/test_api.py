from io import BytesIO
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Aerospace Telemetry Platform"
    }

def test_health_endpoint() -> None:
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }

def test_rejects_non_csv_file() -> None:
    response = client.post(
        "/telemetry",
        files={
            "file": (
                "telemetry.txt",
                BytesIO(b"not telemetry"),
                "text/plain",

            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Upload a CSV file"

def test_processes_valid_telemetry() -> None:
    '''this is hardcoded testing of one file. adjust this so it can verify any file'''
    csv_data = (
        "engine_id,cycle,operational_setting_1,"
        "operational_setting_2,operational_setting_3,"
        "sensor_1,sensor_2,sensor_3\n"
        "1,1,0.1,0.2,100.0,500.0,600.0,700.0\n"
        "1,2,0.1,0.2,100.0,510.0,610.0,710.0\n"
    )

    response = client.post(
        "/telemetry",
        files={
            "file": (
                "telemetry.csv",
                BytesIO(csv_data.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["summary"]["rows"] == 2
    assert payload["summary"]["engines"] == 1
    assert payload["summary"]["min_cycle"] == 1
    assert payload["summary"]["max_cycle"] == 2

def test_rejects_csv_with_missing_columns() -> None:
    invalid_csv = (
        "engine_id,cycle,sensor_1\n"
        "1,1,500.0\n"
    )

    response = client.post(
        "/telemetry",
        files = {
            "file": (
                "invalid.csv",
                BytesIO(invalid_csv.encode("utf-8")),
                "text/csv"
            )
        },
    )

    assert response.status_code == 422
    assert "Missing required columns" in response.json()["detail"]

def test_unknown_result_returns_404() -> None:
    response = client.get("/results/not-a-real-job-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Result not found"