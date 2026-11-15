"""Unit tests for the retrying HTTP helper — a mock transport, no network."""

import asyncio

import httpx
import pytest

from bsos.util.http import get_with_retry


def _client(statuses: list[int]) -> tuple[httpx.AsyncClient, list[int]]:
    served: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        status = statuses[min(len(served), len(statuses) - 1)]
        served.append(status)
        return httpx.Response(status, json={"ok": status == 200})

    return httpx.AsyncClient(transport=httpx.MockTransport(handler)), served


def test_get_with_retry_rides_out_a_transient_failure() -> None:
    """The failure that sank the 2026-11-09 run: one 503 among hundreds of requests."""
    client, served = _client([503, 200])
    response = asyncio.run(get_with_retry(client, "https://example.invalid/x", backoff=0))
    assert response.status_code == 200 and served == [503, 200]


def test_get_with_retry_gives_up_and_passes_other_statuses_through() -> None:
    client, served = _client([503])
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(get_with_retry(client, "https://example.invalid/x", attempts=3, backoff=0))
    assert served == [503, 503, 503]
    client, served = _client([404])
    assert asyncio.run(get_with_retry(client, "https://example.invalid/x", backoff=0)).status_code == 404
    assert served == [404]
