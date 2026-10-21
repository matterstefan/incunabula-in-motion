"""CERL retrieval helpers reused from Prayer Books in Motion."""
from __future__ import annotations
import json, os, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
API_ENDPOINT = "https://data.cerl.org/mei/_search"
PAGE_SIZE = 100
RETRYABLE_HTTP_CODES = {429,500,502,503,504}


def access_user_agent() -> str:
    value = os.environ.get("CERL_USER_AGENT", "").strip()
    if not value or any(ord(char) < 32 or ord(char) > 126 for char in value):
        raise ValueError("Set CERL_USER_AGENT to the access identifier supplied by CERL")
    return value

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    serialized = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    secret = os.environ.get("CERL_USER_AGENT", "").strip()
    if secret and (secret in serialized or json.dumps(secret)[1:-1] in serialized):
        raise ValueError("Output contains the access identifier; refusing to save it")
    temporary.write_text(
        serialized,
        encoding="utf-8",
    )
    os.replace(temporary, path)

def hits_value(response: dict[str, Any]) -> int:
    hits = response.get("hits")
    if isinstance(hits, dict):
        hits = hits.get("value")
    if type(hits) is not int or hits < 0:
        raise ValueError("MEI hits must be an explicit non-negative integer")
    return hits

class RateLimiter:
    def __init__(self, delay_seconds: float) -> None:
        self.delay_seconds = max(2.0, delay_seconds)
        self.last_request_at: float | None = None

    def wait(self) -> None:
        if self.last_request_at is not None:
            elapsed = time.monotonic() - self.last_request_at
            remaining = self.delay_seconds - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self.last_request_at = time.monotonic()

def request_page(
    istc_id: str,
    offset: int,
    page_size: int,
    limiter: RateLimiter,
    retries: int = 4,
) -> dict[str, Any]:
    parameters = urlencode(
        {
            "query": istc_id,
            "_format": "json",
            "nofacets": "true",
            "size": str(page_size),
            "offset": str(offset),
            "mode": "unstored",
        }
    )
    request = Request(
        f"{API_ENDPOINT}?{parameters}",
        headers={
            "User-Agent": access_user_agent(),
            "Accept": "application/json",
        },
    )

    for attempt in range(1, retries + 1):
        limiter.wait()
        try:
            with urlopen(request, timeout=60) as response:
                raw = response.read()
                try:
                    return json.loads(raw)
                except (json.JSONDecodeError, UnicodeDecodeError) as error:
                    raise ValueError(
                        f"MEI returned non-JSON content for {istc_id}; "
                        f"HTTP {response.status}; "
                        f"bytes: {len(raw)}. Response content omitted to protect access details."
                    ) from None
        except HTTPError as error:
            if error.code not in RETRYABLE_HTTP_CODES or attempt == retries:
                raise
            time.sleep(2**attempt)
        except (URLError, TimeoutError):
            if attempt == retries:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("Unreachable retry state")

def fetch_complete_query(
    istc_id: str,
    limiter: RateLimiter,
    page_size: int = PAGE_SIZE,
) -> dict[str, Any]:
    if not 1 <= page_size <= 100:
        raise ValueError("MEI search page size must be between 1 and 100")

    rows: list[dict[str, Any]] = []
    seen_record_ids: set[str] = set()
    offset = 0
    reported_hits: int | None = None

    while reported_hits is None or offset < reported_hits:
        response = request_page(istc_id, offset, page_size, limiter)
        if not isinstance(response, dict) or "hits" not in response:
            fields = ", ".join(str(key)[:60] for key in list(response)[:20]) if isinstance(response, dict) else type(response).__name__
            secret = os.environ.get("CERL_USER_AGENT", "").strip()
            if secret:
                fields = fields.replace(secret, "[redacted]")
            raise ValueError(f"MEI response lacks explicit hit count for {istc_id}; response fields/type: {fields}")
        page_hits = hits_value(response)
        if "rows" not in response and page_hits != 0:
            raise ValueError(f"MEI reports {page_hits} hits but supplies no rows for {istc_id}")
        if reported_hits is None:
            reported_hits = page_hits
        elif page_hits != reported_hits:
            raise RuntimeError(
                f"MEI hit count changed during paginated query for {istc_id}: "
                f"{reported_hits} to {page_hits}"
            )

        page_rows = response.get("rows", [])
        if not isinstance(page_rows, list):
            raise ValueError(f"Unexpected rows value for {istc_id}")
        if not page_rows and offset < reported_hits:
            raise RuntimeError(
                f"MEI returned an empty page for {istc_id} at offset {offset} "
                f"before the reported {reported_hits} hits were retrieved"
            )

        new_rows = 0
        for record in page_rows:
            record_id = str(record.get("id", ""))
            if not record_id:
                raise ValueError(f"MEI result without id for {istc_id}")
            if record_id in seen_record_ids:
                continue
            seen_record_ids.add(record_id)
            rows.append(record)
            new_rows += 1
        if page_rows and new_rows == 0:
            raise RuntimeError(
                f"Pagination for {istc_id} made no progress at offset {offset}"
            )
        offset += len(page_rows)

    if len(rows) != reported_hits:
        raise RuntimeError(
            f"MEI reported {reported_hits} hits for {istc_id}, "
            f"but {len(rows)} distinct records were retrieved"
        )

    return {
        "retrieved_at": now_iso(),
        "endpoint": API_ENDPOINT,
        "query": istc_id,
        "page_size": page_size,
        "reported_hits": reported_hits,
        "rows": rows,
    }
