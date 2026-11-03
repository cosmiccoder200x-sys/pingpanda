"""Resolving hosts and checking URLs asynchronously."""

from __future__ import annotations

import asyncio
import socket
import time
from urllib.parse import urlparse

import httpx
from tqdm import tqdm

from pingpanda.models import UrlResult

DEFAULT_TIMEOUT_SECONDS = 10.0


def resolve_ip_and_port(url):
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        scheme = parsed.scheme
        port = parsed.port or (443 if scheme == "https" else 8080)
        ip_address = socket.gethostbyname(hostname)
        return f"{ip_address}:{port}"
    except Exception:
        return "IP:Port Not Found"


def normalize_url(url):
    url = url.strip()
    if "://" not in url:
        url = "http://" + url
    return url


async def check_url_status(session, url_id, url):
    url = normalize_url(url)
    started = time.perf_counter()
    try:
        response = await session.get(
            url,
            follow_redirects=True,
            timeout=httpx.Timeout(DEFAULT_TIMEOUT_SECONDS, read=None),
        )
    except httpx.ConnectError:
        elapsed = time.perf_counter() - started
        return UrlResult(url_id, url, None, elapsed, None, "IP:Port Not Found", None)

    final_url = str(response.url)
    original_ip_port = resolve_ip_and_port(url)
    redirect_ip_port = resolve_ip_and_port(final_url) if final_url != url else None
    redirect_to = final_url if final_url != url else None

    elapsed = time.perf_counter() - started
    return UrlResult(
        url_id,
        url,
        response.status_code,
        elapsed,
        redirect_to,
        original_ip_port,
        redirect_ip_port,
    )


async def check_all(urls, initial_results=None, on_result=None):
    """Check unfinished URLs and optionally persist each newly completed result.

    URL IDs always refer to the original input order. Existing checkpoint results
    are retained and are not requested again.
    """
    urls = list(urls)
    results = dict(initial_results or {})

    for url_id, result in results.items():
        if (
            isinstance(url_id, bool)
            or not isinstance(url_id, int)
            or not 0 <= url_id < len(urls)
            or result.url_id != url_id
            or result.url != normalize_url(urls[url_id])
        ):
            raise ValueError(f"Initial result {url_id!r} does not match the URL list.")

    pending = [
        (url_id, url)
        for url_id, url in enumerate(urls)
        if url_id not in results
    ]
    if not pending:
        return dict(sorted(results.items()))

    progress = tqdm(
        total=len(urls),
        initial=len(results),
        desc="Checking URLs",
    ) if len(urls) > 1 else None

    tasks = []
    try:
        async with httpx.AsyncClient() as session:
            tasks = [
                asyncio.create_task(check_url_status(session, url_id, url))
                for url_id, url in pending
            ]
            for completed_task in asyncio.as_completed(tasks):
                result = await completed_task
                results[result.url_id] = result
                if on_result is not None:
                    on_result(dict(results))
                if progress is not None:
                    progress.update(1)
    except BaseException:
        for task in tasks:
            if not task.done():
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        raise
    finally:
        if progress is not None:
            progress.close()

    return dict(sorted(results.items()))
