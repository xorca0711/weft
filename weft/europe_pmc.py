"""Bounded Europe PMC metadata retrieval. No model, full text or scientific runs."""
from __future__ import annotations

from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
MAX_BYTES = 8 * 1024 * 1024


class SourceError(ValueError):
    pass


def date_window(query: str, field: str, since: str, until: str) -> str:
    if field not in {"FIRST_IDATE", "FIRST_PDATE"}:
        raise SourceError("Only first-indexed and first-publication windows are supported")
    start, end = date.fromisoformat(since), date.fromisoformat(until)
    if start > end:
        raise SourceError("Window start is after its end")
    if not query.strip() or len(query) > 6000:
        raise SourceError("A bounded, nonempty query is required")
    return f"({query}) AND {field}:[{start.isoformat()} TO {end.isoformat()}]"


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Weft/0.2 (+https://github.com/xorca0711/weft)",
                                    "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise SourceError("Metadata response exceeds the 8 MiB limit")
    return body


class EuropePMC:
    def __init__(self, fetch=download, sleep=time.sleep, attempts=3):
        if not 1 <= attempts <= 3:
            raise ValueError("Use one to three transport attempts")
        self.fetch, self.sleep, self.attempts = fetch, sleep, attempts

    def request(self, url: str):
        attempts = []
        for number in range(1, self.attempts + 1):
            try:
                body = self.fetch(url)
                attempts.append({"attempt": number, "status": 200})
                return body, attempts
            except (HTTPError, URLError, TimeoutError) as exc:
                code = exc.code if isinstance(exc, HTTPError) else None
                attempts.append({"attempt": number, "status": code,
                                 "error_type": type(exc).__name__})
                retryable = code is None or code == 429 or code in {500, 502, 503, 504}
                if not retryable or number == self.attempts:
                    error = SourceError(f"Europe PMC transport failed ({code or type(exc).__name__})")
                    error.attempts = attempts
                    raise error from exc
                delay = float(2 ** (number - 1))
                if isinstance(exc, HTTPError) and exc.headers:
                    retry_after = exc.headers.get("Retry-After")
                    if retry_after:
                        try:
                            delay = float(retry_after)
                        except ValueError:
                            try:
                                delay = (parsedate_to_datetime(retry_after)
                                         - datetime.now(timezone.utc)).total_seconds()
                            except (ValueError, TypeError):
                                pass
                self.sleep(max(0, min(delay, 20)))

    def search(self, query: str, on_page, *, page_size=100, max_records=200):
        if type(page_size) is not int or type(max_records) is not int:
            raise SourceError("Integer request bounds required")
        if not 1 <= page_size <= 1000 or not 1 <= max_records <= 10000:
            raise SourceError("Invalid retrieval bounds")
        cursor, visited, seen_ids = "*", set(), set()
        records, total, page_no, warnings = [], None, 0, []
        while True:
            if cursor in visited:
                raise SourceError("Pagination cursor repeated")
            visited.add(cursor)
            size = min(page_size, max_records - len(records))
            params = {"query": query, "format": "json", "resultType": "core",
                      "pageSize": size, "cursorMark": cursor}
            url = BASE + "/search?" + urlencode(params)
            body, attempts = self.request(url)
            try:
                response = json.loads(body)
                hits = response["hitCount"]
                batch = response["resultList"]["result"]
                if type(hits) is not int or hits < 0 or not isinstance(batch, list):
                    raise ValueError("Unexpected hitCount or result array")
                if len(batch) > size:
                    raise ValueError("Server exceeded requested page size")
                for record in batch:
                    if not isinstance(record, dict) or not record.get("source") or not record.get("id"):
                        raise ValueError("Record lacks provider identity")
            except (KeyError, TypeError, ValueError) as exc:
                # Preserve even malformed responses as evidence of failure.
                on_page({"page": page_no + 1, "url": url, "cursor": cursor,
                         "next_cursor": None, "attempts": attempts, "malformed": True}, body)
                raise SourceError("Malformed Europe PMC search response") from exc
            page_no += 1
            next_cursor = response.get("nextCursorMark")
            on_page({"page": page_no, "url": url, "cursor": cursor,
                     "next_cursor": next_cursor, "hit_count": hits,
                     "records": len(batch), "api_version": response.get("version"),
                     "attempts": attempts}, body)
            if total is None:
                total = hits
            elif total != hits:
                if "hit-count-changed-during-pagination" not in warnings:
                    warnings.append("hit-count-changed-during-pagination")
            for record in batch:
                identity = (str(record["source"]), str(record["id"]))
                if identity in seen_ids and "duplicate-provider-record-in-pages" not in warnings:
                    warnings.append("duplicate-provider-record-in-pages")
                seen_ids.add(identity)
            records.extend(batch)
            if len(records) >= hits and (not next_cursor or len(batch) < size or len(records) == hits):
                break
            if len(records) >= max_records:
                return {"status": "truncated", "hit_count": total, "records": records,
                        "pages": page_no, "warnings": warnings, "next_cursor": next_cursor}
            if not batch or not next_cursor:
                raise SourceError("Incomplete pagination: records remain but continuation is missing")
            cursor = next_cursor
        return {"status": "unstable" if warnings else "complete", "hit_count": total,
                "records": records, "pages": page_no, "warnings": warnings, "next_cursor": None}
