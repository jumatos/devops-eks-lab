from uuid import uuid4

from fastapi.testclient import TestClient
from prometheus_client.parser import text_string_to_metric_families

from app.main import app


def read_metrics(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")

    return [
        sample
        for family in text_string_to_metric_families(response.text)
        for sample in family.samples
    ]


def sample_value(samples, name, labels):
    for sample in samples:
        if sample.name == name and sample.labels == labels:
            return sample.value

    return 0.0


def test_metrics_record_request_and_duration():
    request_labels = {
        "method": "GET",
        "route": "/health",
        "status_code": "200",
    }
    duration_labels = {
        "method": "GET",
        "route": "/health",
    }

    with TestClient(app) as client:
        before = read_metrics(client)

        assert client.get("/health").status_code == 200

        after = read_metrics(client)

    assert sample_value(
        after, "task_api_http_requests_total", request_labels
    ) == sample_value(
        before, "task_api_http_requests_total", request_labels
    ) + 1

    assert sample_value(
        after,
        "task_api_http_request_duration_seconds_count",
        duration_labels,
    ) == sample_value(
        before,
        "task_api_http_request_duration_seconds_count",
        duration_labels,
    ) + 1

    assert sample_value(
        after,
        "task_api_http_request_duration_seconds_sum",
        duration_labels,
    ) > sample_value(
        before,
        "task_api_http_request_duration_seconds_sum",
        duration_labels,
    )


def test_metrics_group_task_ids_under_route_template(client):
    labels = {
        "method": "GET",
        "route": "/tasks/{task_id}",
        "status_code": "404",
    }

    before = read_metrics(client)
    task_ids = [str(uuid4()), str(uuid4())]

    for task_id in task_ids:
        assert client.get(f"/tasks/{task_id}").status_code == 404

    after = read_metrics(client)

    assert sample_value(
        after, "task_api_http_requests_total", labels
    ) == sample_value(
        before, "task_api_http_requests_total", labels
    ) + 2

    routes = {sample.labels.get("route") for sample in after}

    for task_id in task_ids:
        assert f"/tasks/{task_id}" not in routes


def test_metrics_group_unknown_routes():
    labels = {
        "method": "GET",
        "route": "unmatched",
        "status_code": "404",
    }

    with TestClient(app) as client:
        before = read_metrics(client)

        for _ in range(2):
            assert client.get(f"/unknown-{uuid4()}").status_code == 404

        after = read_metrics(client)

    assert sample_value(
        after, "task_api_http_requests_total", labels
    ) == sample_value(
        before, "task_api_http_requests_total", labels
    ) + 2


def test_metrics_scrapes_do_not_count_themselves():
    with TestClient(app) as client:
        before = read_metrics(client)
        after = read_metrics(client)

    assert after == before
    assert all(
        sample.labels.get("route") != "/metrics"
        for sample in after
    )