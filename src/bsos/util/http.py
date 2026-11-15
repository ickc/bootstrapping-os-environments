from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Iterable, TypeVar

import httpx

T = TypeVar("T")
R = TypeVar("R")

#: Statuses worth retrying: rate limiting and transient server-side failures.
TRANSIENT_STATUS: frozenset[int] = frozenset({429, 500, 502, 503, 504})


async def get_with_retry(
    client: httpx.AsyncClient,
    url: str,
    *,
    attempts: int = 5,
    backoff: float = 1.0,
) -> httpx.Response:
    """GET *url*, retrying transient failures with exponential backoff
    (*backoff* seconds, doubling each time).

    Transient means a connection-level error or a status in
    :data:`TRANSIENT_STATUS`; a single hiccup from a public API must not sink
    a run that makes hundreds of requests. Any other status is returned as-is
    (the caller decides whether a 404 is an error), and the last transient
    failure is raised once *attempts* are exhausted.
    """
    for attempt in range(attempts):
        last = attempt == attempts - 1
        try:
            response = await client.get(url)
        except httpx.TransportError:
            if last:
                raise
        else:
            if response.status_code not in TRANSIENT_STATUS:
                return response
            if last:
                response.raise_for_status()
        await asyncio.sleep(backoff * 2**attempt)
    raise AssertionError("unreachable")  # pragma: no cover


async def gather_limited(
    items: Iterable[T],
    worker: Callable[[T], Awaitable[R]],
    *,
    concurrency: int = 16,
) -> list[R]:
    """Run *worker* over *items* concurrently, at most *concurrency* at a time.

    Results come back in input order. Bounding the fan-out keeps a batch of
    hundreds of requests from looking like a burst to the server.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def run(item: T) -> R:
        async with semaphore:
            return await worker(item)

    return list(await asyncio.gather(*(run(item) for item in items)))
