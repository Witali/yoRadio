#!/usr/bin/env python3
"""
Collect and verify direct internet-radio streams for:

* Radio Record
* 101.ru
* Zaycev.FM
* Relax FM
* Radio Caprice (RADCAP)

The collector uses three layers:

1. Crawl public HTML/JSON/JavaScript and extract stream-like URLs.
2. Apply site-specific URL templates where the site exposes channel IDs/slugs.
3. Optionally query the public Radio Browser directory as a fallback.

Outputs:

* streams.json          full structured result
* streams_report.csv    full verification report
* playlist.m3u          playable M3U playlist
* playlist.csv          tab-separated yoRadio playlist (name<TAB>url<TAB>ovol)

Python 3.11+; dependency: httpx

Examples:

    python radio_stream_collector.py --verify
    python radio_stream_collector.py --sites record,zaycev --quality low --verify
    python radio_stream_collector.py --sites 101 --max-101-channels 100 --verify
    python radio_stream_collector.py --no-radio-browser --include-unverified

Notes:

* The script reads public pages only. It does not bypass authentication, CAPTCHA,
  geo-blocking, or DRM.
* Direct stream URLs are operational data and can change at any time.
* Do not use HEAD as the only test: many Icecast/Shoutcast servers support GET
  but reject HEAD. This script performs a small streaming GET and then closes it.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import html
import json
import logging
import re
import socket
import ssl
import sys
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

try:
    import httpx
except ImportError as exc:  # pragma: no cover - friendly startup error
    raise SystemExit(
        "Missing dependency 'httpx'. Install it with:\n"
        "    python -m pip install 'httpx>=0.27,<1'"
    ) from exc


VERSION = "1.0.0"
DEFAULT_USER_AGENT = f"yoRadio-stream-collector/{VERSION} (+local playlist utility)"

AUDIO_EXTENSIONS = {
    ".mp3": "MP3",
    ".aac": "AAC",
    ".aacp": "AAC",
    ".m4a": "AAC/M4A",
    ".ogg": "Ogg",
    ".opus": "Opus",
    ".flac": "FLAC",
    ".wav": "WAV",
    ".weba": "WebM audio",
}
PLAYLIST_EXTENSIONS = {".m3u", ".m3u8", ".pls", ".asx", ".xspf"}
AUDIO_MIME_PREFIXES = ("audio/",)
AUDIO_MIME_EXACT = {
    "application/ogg",
    "application/octet-stream",
    "video/mp2t",  # HLS transport stream
}
PLAYLIST_MIMES = {
    "application/vnd.apple.mpegurl",
    "application/x-mpegurl",
    "audio/mpegurl",
    "audio/x-mpegurl",
    "application/mpegurl",
    "application/pls+xml",
    "audio/x-scpls",
    "video/x-ms-asf",
    "application/xspf+xml",
}
REJECT_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico",
    ".css", ".woff", ".woff2", ".ttf", ".map", ".pdf", ".zip",
    ".apk", ".exe", ".dmg", ".webmanifest",
}
STREAM_PATH_HINTS = (
    "/stream", "/listen", "/live", "/radio", "/icecast", "/shoutcast",
    "/aac/", "/mp3/", "/hls/", "/playlist", "/fm", "/air/",
)
STREAM_HOST_HINTS = (
    "hostingradio.ru", "cdnvideo.ru", "zaycev.fm", "101.ru", "gpmradio.ru",
    "myradio24.com", "streamr.ru", "radiorecord.ru", "radcap.ru",
)
URL_RE = re.compile(r"(?:(?:https?:)?//)[^\s\"'<>\\]+", re.IGNORECASE)
CHANNEL_101_RE = re.compile(r"/radio/channel/(\d+)(?:\D|$)")
RECORD_STATION_RE = re.compile(r"/station/([a-zA-Z0-9_-]+)(?:[/?#]|$)")
RELAX_CHANNEL_RE = re.compile(r"/channels/(\d+)(?:\D|$)")


@dataclass(slots=True)
class SiteSpec:
    key: str
    title: str
    seeds: tuple[str, ...]
    page_hosts: tuple[str, ...]
    follow_patterns: tuple[str, ...]
    stream_hosts: tuple[str, ...]
    radio_browser_queries: tuple[str, ...]
    max_pages_default: int = 120
    max_assets_default: int = 60


SITE_SPECS: dict[str, SiteSpec] = {
    "record": SiteSpec(
        key="record",
        title="Radio Record",
        seeds=("https://www.radiorecord.ru/stations",),
        page_hosts=("radiorecord.ru",),
        follow_patterns=(r"^/stations/?$", r"^/station/[a-zA-Z0-9_-]+/?$"),
        stream_hosts=("radiorecord.hostingradio.ru",),
        radio_browser_queries=("Radio Record",),
        max_pages_default=180,
    ),
    "101": SiteSpec(
        key="101",
        title="101.ru",
        seeds=("https://101.ru/",),
        page_hosts=("101.ru",),
        follow_patterns=(r"^/$", r"^/radio/channel/\d+/?$"),
        stream_hosts=("101.ru", "gpmradio.ru"),
        radio_browser_queries=("101.ru", "101 RU"),
        max_pages_default=350,
        max_assets_default=80,
    ),
    "zaycev": SiteSpec(
        key="zaycev",
        title="Zaycev.FM",
        seeds=("https://www.zaycev.fm/",),
        page_hosts=("zaycev.fm",),
        follow_patterns=(r"^/$", r"^/[a-zA-Z0-9_-]+/?$"),
        stream_hosts=("zaycev.fm",),
        radio_browser_queries=("Zaycev.FM", "Zaycev FM"),
        max_pages_default=60,
    ),
    "relax": SiteSpec(
        key="relax",
        title="Relax FM",
        seeds=("https://relax-fm.ru/channels",),
        page_hosts=("relax-fm.ru",),
        follow_patterns=(r"^/channels/?$", r"^/channels/\d+/?$"),
        stream_hosts=("relax-fm.ru", "101.ru", "gpmradio.ru", "hostingradio.ru"),
        radio_browser_queries=("Relax FM",),
        max_pages_default=80,
    ),
    "caprice": SiteSpec(
        key="caprice",
        title="Radio Caprice",
        seeds=(
            "https://radcap.ru/index-d.html",
            "https://radcap.ru/electronic-d.html",
            "https://radcap.ru/rock-d.html",
            "https://radcap.ru/jazz-d.html",
            "https://radcap.ru/classical-d.html",
            "https://radcap.ru/pop-d.html",
            "https://radcap.ru/hiphop-d.html",
        ),
        page_hosts=("radcap.ru",),
        follow_patterns=(r"^/[a-zA-Z0-9_-]+-[dm]\.html$", r"^/index-[dm]\.html$"),
        stream_hosts=("radcap.ru",),
        radio_browser_queries=("Radio Caprice", "RADCAP"),
        max_pages_default=650,
        max_assets_default=100,
    ),
}


@dataclass(slots=True)
class Candidate:
    site: str
    name: str
    url: str
    source_page: str = ""
    discovered_by: str = "crawl"
    alternatives: list[str] = field(default_factory=list)
    codec_hint: str = ""
    bitrate_hint: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProbeResult:
    ok: bool
    requested_url: str
    resolved_url: str = ""
    status_code: int = 0
    content_type: str = ""
    codec: str = ""
    bitrate_kbps: int = 0
    bytes_read: int = 0
    is_playlist: bool = False
    playlist_entries: list[str] = field(default_factory=list)
    icy_name: str = ""
    icy_bitrate: int = 0
    elapsed_ms: int = 0
    error: str = ""


@dataclass(slots=True)
class FinalStream:
    site: str
    name: str
    url: str
    ok: bool
    status_code: int
    content_type: str
    codec: str
    bitrate_kbps: int
    bytes_read: int
    icy_name: str
    source_page: str
    discovered_by: str
    checked_at: str
    elapsed_ms: int
    error: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CrawlResult:
    candidates: list[Candidate] = field(default_factory=list)
    pages: dict[str, str] = field(default_factory=dict)  # URL -> title
    links: set[str] = field(default_factory=set)
    errors: list[str] = field(default_factory=list)


class PageParser(HTMLParser):
    """Small dependency-free HTML scanner."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.assets: list[str] = []
        self.json_blocks: list[str] = []
        self._in_title = False
        self._title_parts: list[str] = []
        self._in_json_script = False
        self._json_parts: list[str] = []
        self.meta_title = ""

    @property
    def title(self) -> str:
        value = self.meta_title or " ".join(self._title_parts)
        return clean_title(value)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        elif tag == "a" and attr.get("href"):
            self.links.append(attr["href"])
        elif tag in {"script", "iframe", "audio", "source"} and attr.get("src"):
            self.assets.append(attr["src"])
        elif tag == "link" and attr.get("href"):
            rel = attr.get("rel", "").lower()
            typ = attr.get("type", "").lower()
            href = attr["href"]
            if "preload" in rel or "modulepreload" in rel or "json" in typ or href.endswith((".js", ".json")):
                self.assets.append(href)
        elif tag == "meta":
            prop = (attr.get("property") or attr.get("name") or "").lower()
            if prop in {"og:title", "twitter:title"} and attr.get("content"):
                self.meta_title = attr["content"]
        if tag == "script":
            typ = attr.get("type", "").lower()
            if "json" in typ:
                self._in_json_script = True
                self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_json_script:
            self._in_json_script = False
            block = "".join(self._json_parts).strip()
            if block:
                self.json_blocks.append(block)
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data.strip())
        if self._in_json_script:
            self._json_parts.append(data)


class RateLimiter:
    def __init__(self, delay_seconds: float) -> None:
        self.delay = max(0.0, delay_seconds)
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def wait(self) -> None:
        if self.delay <= 0:
            return
        async with self._lock:
            now = time.monotonic()
            wait_for = self.delay - (now - self._last)
            if wait_for > 0:
                await asyncio.sleep(wait_for)
            self._last = time.monotonic()


class StreamCollector:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.logger = logging.getLogger("radio-stream-collector")
        limits = httpx.Limits(
            max_connections=max(10, args.concurrency * 2),
            max_keepalive_connections=max(5, args.concurrency),
        )
        timeout = httpx.Timeout(
            connect=args.timeout,
            read=args.timeout,
            write=args.timeout,
            pool=args.timeout,
        )
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": args.user_agent,
                "Accept": "*/*",
                "Accept-Language": "ru,en;q=0.7",
            },
            follow_redirects=True,
            timeout=timeout,
            limits=limits,
            verify=not args.insecure,
        )
        self.rate_limiter = RateLimiter(args.delay)
        self.probe_semaphore = asyncio.Semaphore(args.concurrency)
        self._probe_cache: dict[str, ProbeResult] = {}

    async def close(self) -> None:
        await self.client.aclose()

    async def run(self, site_keys: Sequence[str]) -> list[FinalStream]:
        all_candidates: list[Candidate] = []
        crawl_results: dict[str, CrawlResult] = {}

        for key in site_keys:
            spec = SITE_SPECS[key]
            self.logger.info("Collecting %s", spec.title)
            result = await self.crawl_site(spec)
            crawl_results[key] = result
            all_candidates.extend(result.candidates)
            all_candidates.extend(self.derive_site_candidates(spec, result))
            self.logger.info(
                "%s: %d pages, %d raw candidates",
                spec.title,
                len(result.pages),
                len(result.candidates),
            )

        if self.args.radio_browser:
            self.logger.info("Querying Radio Browser fallback")
            for key in site_keys:
                all_candidates.extend(await self.collect_radio_browser(SITE_SPECS[key]))

        candidates = merge_candidates(all_candidates)
        self.logger.info("%d unique candidates before verification", len(candidates))

        if not self.args.verify:
            checked_at = utc_now()
            return [
                FinalStream(
                    site=c.site,
                    name=c.name,
                    url=c.url,
                    ok=False,
                    status_code=0,
                    content_type="",
                    codec=c.codec_hint,
                    bitrate_kbps=c.bitrate_hint,
                    bytes_read=0,
                    icy_name="",
                    source_page=c.source_page,
                    discovered_by=c.discovered_by,
                    checked_at=checked_at,
                    elapsed_ms=0,
                    error="not verified",
                    metadata=c.metadata,
                )
                for c in candidates
            ]

        tasks = [asyncio.create_task(self.verify_candidate(c)) for c in candidates]
        verified: list[FinalStream] = []
        completed = 0
        for task in asyncio.as_completed(tasks):
            try:
                stream = await task
                verified.append(stream)
            except Exception as exc:  # defensive; per-candidate errors should be contained
                self.logger.exception("Unexpected verification error: %s", exc)
            completed += 1
            if completed % 25 == 0 or completed == len(tasks):
                self.logger.info("Verified %d/%d", completed, len(tasks))

        verified = choose_best_per_station(verified)
        verified.sort(key=lambda x: (x.site.lower(), x.name.lower(), not x.ok, x.url))
        return verified

    async def fetch_text(self, url: str) -> tuple[str, str, int]:
        await self.rate_limiter.wait()
        headers = {"Accept": "text/html,application/json,text/javascript,*/*;q=0.5"}
        async with self.client.stream("GET", url, headers=headers) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            encoding = response.encoding or "utf-8"
            data = bytearray()
            async for chunk in response.aiter_bytes():
                data.extend(chunk)
                if len(data) >= self.args.max_text_bytes:
                    break
            payload = bytes(data[: self.args.max_text_bytes])
            status_code = response.status_code
        try:
            text = payload.decode(encoding, errors="replace")
        except LookupError:
            text = payload.decode("utf-8", errors="replace")
        return text, content_type, status_code

    async def crawl_site(self, spec: SiteSpec) -> CrawlResult:
        result = CrawlResult()
        page_limit = self.args.max_pages or spec.max_pages_default
        asset_limit = self.args.max_assets or spec.max_assets_default

        page_queue: deque[str] = deque(spec.seeds)
        asset_queue: deque[tuple[str, str]] = deque()
        visited_pages: set[str] = set()
        visited_assets: set[str] = set()

        while page_queue and len(visited_pages) < page_limit:
            url = canonical_page_url(page_queue.popleft())
            if url in visited_pages:
                continue
            visited_pages.add(url)
            try:
                text, content_type, _ = await self.fetch_text(url)
            except Exception as exc:
                message = f"{spec.key}: {url}: {type(exc).__name__}: {exc}"
                result.errors.append(message)
                self.logger.debug(message)
                continue

            decoded = decode_embedded_text(text)
            parser = PageParser()
            try:
                parser.feed(decoded)
            except Exception as exc:
                self.logger.debug("HTML parse issue at %s: %s", url, exc)

            title = parser.title or guess_name_from_url(url)
            result.pages[url] = title

            result.candidates.extend(
                candidates_from_text(
                    decoded,
                    base_url=url,
                    site=spec.key,
                    page_title=title,
                    source_page=url,
                    stream_hosts=spec.stream_hosts,
                    discovered_by="page-scan",
                )
            )

            for block in parser.json_blocks:
                result.candidates.extend(
                    candidates_from_json_block(
                        block,
                        base_url=url,
                        site=spec.key,
                        page_title=title,
                        source_page=url,
                        stream_hosts=spec.stream_hosts,
                    )
                )

            for raw_link in parser.links:
                linked = clean_joined_url(url, raw_link)
                if not linked:
                    continue
                result.links.add(linked)
                if looks_like_stream(linked, spec.stream_hosts):
                    result.candidates.append(
                        Candidate(
                            site=spec.key,
                            name=title or guess_name_from_url(linked),
                            url=linked,
                            source_page=url,
                            discovered_by="html-link",
                        )
                    )
                elif should_follow_page(linked, spec):
                    page_queue.append(linked)

            for raw_asset in parser.assets:
                asset = clean_joined_url(url, raw_asset)
                if not asset:
                    continue
                if looks_like_stream(asset, spec.stream_hosts):
                    result.candidates.append(
                        Candidate(
                            site=spec.key,
                            name=title or guess_name_from_url(asset),
                            url=asset,
                            source_page=url,
                            discovered_by="media-tag",
                        )
                    )
                elif should_fetch_asset(asset, spec):
                    asset_queue.append((asset, url))

        while asset_queue and len(visited_assets) < asset_limit:
            asset_url, source_page = asset_queue.popleft()
            asset_url = canonical_page_url(asset_url)
            if asset_url in visited_assets:
                continue
            visited_assets.add(asset_url)
            try:
                text, _, _ = await self.fetch_text(asset_url)
            except Exception as exc:
                self.logger.debug("Asset fetch failed %s: %s", asset_url, exc)
                continue
            decoded = decode_embedded_text(text)
            source_title = result.pages.get(source_page, spec.title)
            result.candidates.extend(
                candidates_from_text(
                    decoded,
                    base_url=asset_url,
                    site=spec.key,
                    page_title=source_title,
                    source_page=source_page,
                    stream_hosts=spec.stream_hosts,
                    discovered_by="asset-scan",
                )
            )

        return result

    def derive_site_candidates(self, spec: SiteSpec, crawl: CrawlResult) -> list[Candidate]:
        if spec.key == "record":
            return derive_record_candidates(crawl, self.args.quality)
        if spec.key == "101":
            return derive_101_candidates(crawl, self.args.quality, self.args.max_101_channels)
        if spec.key == "zaycev":
            return derive_zaycev_candidates(crawl, self.args.quality)
        # Relax FM and Radio Caprice generally publish stream data in page/JS;
        # Radio Browser is used as a fallback if static extraction misses it.
        return []

    async def collect_radio_browser(self, spec: SiteSpec) -> list[Candidate]:
        results: list[Candidate] = []
        api_hosts = (
            "https://de1.api.radio-browser.info",
            "https://de2.api.radio-browser.info",
            "https://fi1.api.radio-browser.info",
            "https://nl1.api.radio-browser.info",
        )
        for query in spec.radio_browser_queries:
            payload: list[dict[str, Any]] | None = None
            params = {
                "name": query,
                "hidebroken": "true",
                "limit": str(self.args.radio_browser_limit),
                "order": "lastchecktime",
                "reverse": "true",
            }
            for host in api_hosts:
                endpoint = f"{host}/json/stations/search"
                try:
                    await self.rate_limiter.wait()
                    response = await self.client.get(endpoint, params=params, headers={"Accept": "application/json"})
                    response.raise_for_status()
                    obj = response.json()
                    if isinstance(obj, list):
                        payload = obj
                        break
                except Exception as exc:
                    self.logger.debug("Radio Browser %s failed: %s", host, exc)
            if payload is None:
                continue

            for item in payload:
                url = str(item.get("url_resolved") or item.get("url") or "").strip()
                if not url:
                    continue
                name = str(item.get("name") or query).strip()
                homepage = str(item.get("homepage") or "").strip()
                haystack = " ".join((name, homepage, url)).lower()
                if not radio_browser_matches_site(spec.key, haystack):
                    continue
                if intish(item.get("lastcheckok")) != 1 and not self.args.include_unverified:
                    continue
                results.append(
                    Candidate(
                        site=spec.key,
                        name=name,
                        url=url,
                        source_page=homepage,
                        discovered_by="radio-browser",
                        codec_hint=str(item.get("codec") or ""),
                        bitrate_hint=intish(item.get("bitrate")),
                        metadata={
                            "stationuuid": item.get("stationuuid", ""),
                            "country": item.get("country", ""),
                            "language": item.get("language", ""),
                            "tags": item.get("tags", ""),
                            "radio_browser_lastchecktime": item.get("lastchecktime", ""),
                        },
                    )
                )
        return results

    async def verify_candidate(self, candidate: Candidate) -> FinalStream:
        urls = unique_preserve([candidate.url, *candidate.alternatives])
        best: ProbeResult | None = None
        for url in urls:
            result = await self.probe_url(url, depth=0)
            if best is None or probe_score(result) > probe_score(best):
                best = result
            if result.ok:
                break
        assert best is not None
        display_name = candidate.name
        if normalize_station_name(display_name) in {"radio", "stream", "live", "online"} and best.icy_name.strip():
            display_name = best.icy_name.strip()
        return FinalStream(
            site=candidate.site,
            name=display_name,
            url=best.resolved_url or best.requested_url,
            ok=best.ok,
            status_code=best.status_code,
            content_type=best.content_type,
            codec=best.codec or candidate.codec_hint,
            bitrate_kbps=best.bitrate_kbps or best.icy_bitrate or candidate.bitrate_hint,
            bytes_read=best.bytes_read,
            icy_name=best.icy_name,
            source_page=candidate.source_page,
            discovered_by=candidate.discovered_by,
            checked_at=utc_now(),
            elapsed_ms=best.elapsed_ms,
            error=best.error,
            metadata=candidate.metadata,
        )

    async def probe_url(self, url: str, depth: int) -> ProbeResult:
        key = canonical_stream_url(url)
        cached = self._probe_cache.get(key)
        if cached is not None:
            return cached

        async def perform() -> ProbeResult:
            started = time.monotonic()
            try:
                result = await self._probe_httpx(url, depth)
            except Exception as exc:
                # Some old Shoutcast servers answer with "ICY 200 OK", which
                # strict HTTP clients can reject. Try a small raw-socket probe.
                try:
                    result = await self._probe_raw_icy(url)
                except Exception as raw_exc:
                    result = ProbeResult(
                        ok=False,
                        requested_url=url,
                        elapsed_ms=int((time.monotonic() - started) * 1000),
                        error=f"{type(exc).__name__}: {exc}; raw fallback: {type(raw_exc).__name__}: {raw_exc}",
                    )
            result.elapsed_ms = result.elapsed_ms or int((time.monotonic() - started) * 1000)
            self._probe_cache[key] = result
            return result

        # Recursive playlist probes must not acquire another semaphore slot: if
        # every top-level slot contains a playlist, reacquiring here would deadlock.
        if depth > 0:
            return await perform()
        async with self.probe_semaphore:
            return await perform()

    async def _probe_httpx(self, url: str, depth: int) -> ProbeResult:
        started = time.monotonic()
        headers = {
            "Accept": "*/*",
            "Icy-MetaData": "1",
            "Range": f"bytes=0-{self.args.probe_bytes - 1}",
            "Connection": "close",
        }
        await self.rate_limiter.wait()
        async with self.client.stream("GET", url, headers=headers) as response:
            status = response.status_code
            content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            icy_name = response.headers.get("icy-name", "").strip()
            icy_bitrate = intish(response.headers.get("icy-br"))
            data = bytearray()
            async for chunk in response.aiter_bytes():
                data.extend(chunk)
                if len(data) >= self.args.probe_bytes:
                    break
            body = bytes(data[: self.args.probe_bytes])
            resolved = str(response.url)

        codec = detect_codec(content_type, body, resolved)
        playlist = is_playlist_response(content_type, resolved, body)
        entries: list[str] = []
        if playlist:
            entries = parse_playlist(body, resolved, content_type, self.args.quality)
            if depth < self.args.playlist_depth:
                best_child: ProbeResult | None = None
                for child in entries[: self.args.max_playlist_entries]:
                    child_result = await self.probe_url(child, depth + 1)
                    if best_child is None or probe_score(child_result) > probe_score(best_child):
                        best_child = child_result
                    if child_result.ok:
                        return ProbeResult(
                            ok=True,
                            requested_url=url,
                            resolved_url=child_result.resolved_url or child_result.requested_url,
                            status_code=status,
                            content_type=child_result.content_type or content_type,
                            codec=child_result.codec,
                            bitrate_kbps=child_result.bitrate_kbps,
                            bytes_read=len(body) + child_result.bytes_read,
                            is_playlist=True,
                            playlist_entries=entries,
                            icy_name=child_result.icy_name or icy_name,
                            icy_bitrate=child_result.icy_bitrate or icy_bitrate,
                            elapsed_ms=int((time.monotonic() - started) * 1000),
                        )
                if best_child is not None:
                    return ProbeResult(
                        ok=False,
                        requested_url=url,
                        resolved_url=resolved,
                        status_code=status,
                        content_type=content_type,
                        codec=codec,
                        bytes_read=len(body),
                        is_playlist=True,
                        playlist_entries=entries,
                        icy_name=icy_name,
                        icy_bitrate=icy_bitrate,
                        elapsed_ms=int((time.monotonic() - started) * 1000),
                        error=f"playlist found, child failed: {best_child.error}",
                    )

        ok_status = 200 <= status < 300
        audio_header = content_type.startswith(AUDIO_MIME_PREFIXES) or content_type in AUDIO_MIME_EXACT
        has_stream_header = bool(icy_name or icy_bitrate or response_header_stream_hint(content_type))
        has_audio_magic = codec not in {"", "Playlist", "Unknown"}
        enough_data = len(body) >= min(512, self.args.probe_bytes)
        ok = ok_status and (
            (playlist and bool(entries))
            or audio_header
            or has_stream_header
            or (has_audio_magic and enough_data)
        )
        error = ""
        if not ok:
            if not ok_status:
                error = f"HTTP {status}"
            elif content_type.startswith("text/html"):
                error = "HTML page, not an audio stream"
            elif playlist and not entries:
                error = "empty or unsupported playlist"
            elif not enough_data:
                error = f"only {len(body)} bytes received"
            else:
                error = f"content did not look like audio ({content_type or 'no MIME'})"

        return ProbeResult(
            ok=ok,
            requested_url=url,
            resolved_url=resolved,
            status_code=status,
            content_type=content_type,
            codec=codec,
            bitrate_kbps=icy_bitrate,
            bytes_read=len(body),
            is_playlist=playlist,
            playlist_entries=entries,
            icy_name=icy_name,
            icy_bitrate=icy_bitrate,
            elapsed_ms=int((time.monotonic() - started) * 1000),
            error=error,
        )

    async def _probe_raw_icy(self, url: str) -> ProbeResult:
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"} or not parts.hostname:
            raise ValueError("unsupported URL for raw probe")
        port = parts.port or (443 if parts.scheme == "https" else 80)
        ssl_context: ssl.SSLContext | bool | None
        if parts.scheme == "https":
            ssl_context = ssl.create_default_context()
            if self.args.insecure:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
        else:
            ssl_context = None
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(parts.hostname, port, ssl=ssl_context, server_hostname=parts.hostname if ssl_context else None),
            timeout=self.args.timeout,
        )
        path = urlunsplit(("", "", parts.path or "/", parts.query, ""))
        request = (
            f"GET {path} HTTP/1.0\r\n"
            f"Host: {parts.netloc}\r\n"
            f"User-Agent: {self.args.user_agent}\r\n"
            "Accept: */*\r\n"
            "Icy-MetaData: 1\r\n"
            "Connection: close\r\n\r\n"
        )
        writer.write(request.encode("ascii", errors="ignore"))
        await writer.drain()
        raw = await asyncio.wait_for(reader.read(self.args.probe_bytes + 16384), timeout=self.args.timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

        header_blob, sep, body = raw.partition(b"\r\n\r\n")
        if not sep:
            raise ValueError("no HTTP/ICY header terminator")
        lines = header_blob.decode("latin-1", errors="replace").split("\r\n")
        status_line = lines[0]
        status_match = re.search(r"\s(\d{3})\s", status_line + " ")
        status = int(status_match.group(1)) if status_match else 0
        headers: dict[str, str] = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
        content_type = headers.get("content-type", "").split(";", 1)[0].lower()
        icy_name = headers.get("icy-name", "")
        icy_bitrate = intish(headers.get("icy-br"))
        codec = detect_codec(content_type, body, url)
        ok = 200 <= status < 300 and (
            content_type.startswith("audio/")
            or bool(icy_name)
            or codec not in {"", "Unknown", "Playlist"}
        )
        return ProbeResult(
            ok=ok,
            requested_url=url,
            resolved_url=url,
            status_code=status,
            content_type=content_type,
            codec=codec,
            bitrate_kbps=icy_bitrate,
            bytes_read=len(body),
            icy_name=icy_name,
            icy_bitrate=icy_bitrate,
            error="" if ok else f"raw ICY response did not look like audio: {status_line}",
        )


def decode_embedded_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace(r"\/", "/").replace(r"\u002F", "/").replace(r"\u002f", "/")
    text = text.replace(r"\u003A", ":").replace(r"\u003a", ":")
    text = text.replace(r"\u0026", "&")

    def replace_unicode(match: re.Match[str]) -> str:
        try:
            return chr(int(match.group(1), 16))
        except ValueError:
            return match.group(0)

    return re.sub(r"\\u([0-9a-fA-F]{4})", replace_unicode, text)


def clean_title(value: str) -> str:
    value = re.sub(r"\s+", " ", html.unescape(value or "")).strip(" \t\r\n-|—")
    suffixes = (
        " - слушать онлайн", " — слушать онлайн", " - радио онлайн", " | Radio Record",
        " — радио онлайн. Слушать бесплатно", " - радио онлайн. Слушать бесплатно",
    )
    lowered = value.lower()
    for suffix in suffixes:
        pos = lowered.find(suffix.lower())
        if pos > 0:
            value = value[:pos].strip()
            break
    return value[:180]


def clean_joined_url(base: str, raw: str) -> str:
    raw = html.unescape((raw or "").strip())
    if not raw or raw.startswith(("javascript:", "mailto:", "tel:", "data:", "#")):
        return ""
    raw = raw.replace(r"\/", "/")
    if raw.startswith("//"):
        raw = "https:" + raw
    try:
        url = urljoin(base, raw)
        parts = urlsplit(url)
    except ValueError:
        return ""
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        return ""
    return urlunsplit((parts.scheme, parts.netloc, parts.path or "/", parts.query, ""))


def canonical_page_url(url: str) -> str:
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not k.lower().startswith("utm_") and k.lower() not in {"ysclid", "from"}]
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def canonical_stream_url(url: str) -> str:
    parts = urlsplit(url.strip())
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))


def host_matches(host: str, suffixes: Iterable[str]) -> bool:
    host = (host or "").lower().rstrip(".")
    return any(host == suffix.lower() or host.endswith("." + suffix.lower()) for suffix in suffixes)


def should_follow_page(url: str, spec: SiteSpec) -> bool:
    parts = urlsplit(url)
    if not host_matches(parts.hostname or "", spec.page_hosts):
        return False
    path = parts.path or "/"
    return any(re.search(pattern, path, re.IGNORECASE) for pattern in spec.follow_patterns)


def should_fetch_asset(url: str, spec: SiteSpec) -> bool:
    parts = urlsplit(url)
    if not host_matches(parts.hostname or "", spec.page_hosts):
        return False
    path = parts.path.lower()
    return path.endswith((".js", ".json")) or "/_next/static/" in path or "/assets/" in path or "/build/" in path


def looks_like_stream(url: str, stream_hosts: Iterable[str] = ()) -> bool:
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        return False
    path = (parts.path or "/").lower()
    suffix = Path(path).suffix.lower()
    if suffix in REJECT_EXTENSIONS:
        return False
    if suffix in AUDIO_EXTENSIONS or suffix in PLAYLIST_EXTENSIONS:
        return True
    host = parts.hostname.lower()
    known_host = host_matches(host, tuple(stream_hosts) + STREAM_HOST_HINTS)
    path_hint = any(hint in path for hint in STREAM_PATH_HINTS)
    port_hint = parts.port not in {None, 80, 443}
    # Avoid accepting an ordinary station webpage merely because its domain is known.
    page_like = suffix in {".html", ".htm", ".php"} or path in {"/", "/stations", "/channels"}
    # Non-standard ports are very common for Icecast/Shoutcast and RADCAP
    # streams, including numeric IP hosts. False positives are removed by the
    # subsequent audio probe.
    non_root_path = path not in {"", "/"}
    return not page_like and (
        (known_host and (path_hint or port_hint))
        or (path_hint and port_hint)
        or (port_hint and non_root_path)
    )


def candidates_from_text(
    text: str,
    *,
    base_url: str,
    site: str,
    page_title: str,
    source_page: str,
    stream_hosts: Iterable[str],
    discovered_by: str,
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for match in URL_RE.finditer(text):
        raw = match.group(0).rstrip(").,;]}>")
        url = clean_joined_url(base_url, raw)
        if not url or not looks_like_stream(url, stream_hosts):
            continue
        context = text[max(0, match.start() - 180): min(len(text), match.end() + 180)]
        name = guess_name_from_context(context) or page_title or guess_name_from_url(url)
        candidates.append(
            Candidate(
                site=site,
                name=name,
                url=url,
                source_page=source_page,
                discovered_by=discovered_by,
            )
        )
    return candidates


def candidates_from_json_block(
    block: str,
    *,
    base_url: str,
    site: str,
    page_title: str,
    source_page: str,
    stream_hosts: Iterable[str],
) -> list[Candidate]:
    try:
        obj = json.loads(block)
    except json.JSONDecodeError:
        return candidates_from_text(
            decode_embedded_text(block),
            base_url=base_url,
            site=site,
            page_title=page_title,
            source_page=source_page,
            stream_hosts=stream_hosts,
            discovered_by="json-text-scan",
        )

    found: list[Candidate] = []

    def walk(value: Any, inherited_name: str = "") -> None:
        if isinstance(value, dict):
            local_name = inherited_name
            for key in ("name", "title", "stationName", "channelName", "caption", "label"):
                if isinstance(value.get(key), str) and value[key].strip():
                    local_name = clean_title(value[key])
                    break
            for key, child in value.items():
                if isinstance(child, str) and key.lower() in {
                    "url", "stream", "streamurl", "stream_url", "audio", "audiourl", "audio_url",
                    "src", "listen", "playlist", "file", "href",
                }:
                    url = clean_joined_url(base_url, decode_embedded_text(child))
                    if url and looks_like_stream(url, stream_hosts):
                        found.append(
                            Candidate(
                                site=site,
                                name=local_name or page_title or guess_name_from_url(url),
                                url=url,
                                source_page=source_page,
                                discovered_by="json-structure",
                            )
                        )
                walk(child, local_name)
        elif isinstance(value, list):
            for child in value:
                walk(child, inherited_name)
        elif isinstance(value, str):
            found.extend(
                candidates_from_text(
                    decode_embedded_text(value),
                    base_url=base_url,
                    site=site,
                    page_title=inherited_name or page_title,
                    source_page=source_page,
                    stream_hosts=stream_hosts,
                    discovered_by="json-string",
                )
            )

    walk(obj)
    return found


def guess_name_from_context(context: str) -> str:
    # Common JSON pairs around a stream URL.
    patterns = (
        r'(?i)["\'](?:name|title|stationName|channelName|label)["\']\s*:\s*["\']([^"\']{2,120})["\']',
        r'(?i)data-(?:name|title)=["\']([^"\']{2,120})["\']',
    )
    for pattern in patterns:
        matches = re.findall(pattern, context)
        if matches:
            return clean_title(matches[-1])
    return ""


def guess_name_from_url(url: str) -> str:
    parts = urlsplit(url)
    stem = Path(parts.path.rstrip("/")).name or parts.hostname or "Radio"
    stem = re.sub(r"\.(?:mp3|aacp?|m3u8?|pls|asx|ogg|opus|flac|wav)$", "", stem, flags=re.I)
    stem = re.sub(r"(?:48|64|96|128|192|256|320)k?$", "", stem, flags=re.I)
    stem = re.sub(r"[_-]+", " ", stem).strip()
    return clean_title(stem.title() or "Radio")


def derive_record_candidates(crawl: CrawlResult, quality: str) -> list[Candidate]:
    # Station page slug -> stream token exceptions. Most station slugs already
    # equal their stream token; alternatives are verified before export.
    aliases: dict[str, list[str]] = {
        "record": ["rr_main"],
        "record00": ["2000"],
        "record80": ["1980"],
        "record70": ["1970"],
        "record10": ["2010"],
        "chillout": ["chil"],
        "trancemission": ["tm"],
        "pirate-station": ["ps"],
        "piratestation": ["ps"],
        "superdiscoteka90": ["sd90"],
        "superdiskoteka90": ["sd90"],
        "russian-mix": ["rus"],
        "russianmix": ["rus"],
        "dnb-classics": ["drumhits"],
        "edm-classics": ["edmhits"],
        "old-school": ["pump"],
        "future-house": ["fut"],
        "bass-house": ["jackin"],
    }
    bitrates = quality_bitrates(quality, preferred=96, available=(320, 192, 128, 96, 64))
    output: list[Candidate] = []
    seen_slugs: set[str] = set()
    for link in sorted(crawl.links | set(crawl.pages)):
        match = RECORD_STATION_RE.search(urlsplit(link).path)
        if not match:
            continue
        slug = match.group(1).lower()
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        page = canonical_page_url(link)
        name = crawl.pages.get(page) or crawl.pages.get(link) or f"Radio Record — {slug}"
        tokens = unique_preserve([*aliases.get(slug, []), slug])
        alternatives = [
            f"https://radiorecord.hostingradio.ru/{token}{bitrate}.aacp"
            for token in tokens
            for bitrate in bitrates
        ]
        if not alternatives:
            continue
        output.append(
            Candidate(
                site="record",
                name=name if name.lower().startswith("radio record") else f"Record — {name}",
                url=alternatives[0],
                alternatives=alternatives[1:],
                source_page=page,
                discovered_by="record-template",
                codec_hint="AAC",
                bitrate_hint=bitrates[0],
                metadata={"station_slug": slug},
            )
        )
    return output


def derive_zaycev_candidates(crawl: CrawlResult, quality: str) -> list[Candidate]:
    known_channels = {
        "pop": "Pop", "club": "Club", "newrock": "NewRock", "disco": "Disco",
        "shanson": "Шансон", "rus": "Rus", "rnb": "RnB", "relax": "Relax",
        "zaychata": "Зайчата", "kpop": "K-Pop", "rap": "Rap", "metal": "Metal",
        "bass": "Bass", "love": "Love", "rurock": "РуРок", "folk": "Folk",
        "classic": "Classic",
    }
    token_alias = {"newrock": "rock"}
    slugs: set[str] = set()
    for link in crawl.links | set(crawl.pages):
        parts = urlsplit(link)
        if not host_matches(parts.hostname or "", ("zaycev.fm",)):
            continue
        slug = parts.path.strip("/").lower()
        if slug in known_channels:
            slugs.add(slug)
    if not slugs:
        slugs = set(known_channels)
    bitrates = quality_bitrates(quality, preferred=128, available=(256, 128, 48))
    output: list[Candidate] = []
    for slug in sorted(slugs):
        token = token_alias.get(slug, slug)
        alternatives = [f"https://abs.zaycev.fm/{token}{bitrate}k" for bitrate in bitrates]
        output.append(
            Candidate(
                site="zaycev",
                name=f"Zaycev.FM — {known_channels[slug]}",
                url=alternatives[0],
                alternatives=alternatives[1:],
                source_page=f"https://www.zaycev.fm/{slug}",
                discovered_by="zaycev-template",
                codec_hint="MP3",
                bitrate_hint=bitrates[0],
                metadata={"channel_slug": slug},
            )
        )
    return output


def derive_101_candidates(crawl: CrawlResult, quality: str, max_channels: int) -> list[Candidate]:
    channels: dict[int, tuple[str, str]] = {}
    for link in sorted(crawl.links | set(crawl.pages)):
        parts = urlsplit(link)
        match = CHANNEL_101_RE.search(parts.path)
        if not match:
            continue
        channel_id = int(match.group(1))
        canonical = f"https://101.ru/radio/channel/{channel_id}"
        title = crawl.pages.get(canonical) or crawl.pages.get(canonical_page_url(link)) or f"Канал {channel_id}"
        channels[channel_id] = (title, canonical)
        if len(channels) >= max_channels:
            break

    profiles = (
        [("pro", "aac", 64), ("trust", "mp3", 128)]
        if quality in {"low", "auto"}
        else [("trust", "mp3", 128), ("pro", "aac", 64)]
    )
    bases = (
        "https://pub0101.101.ru:8443",
        "https://pub0201.101.ru:8443",
        "https://pub0202.101.ru:8443",
        "https://pub0301.101.ru:8443",
        "https://pub0302.101.ru:8443",
        "https://srv11.gpmradio.ru:8443",
        "http://pub0101.101.ru:8000",
        "http://pub0201.101.ru:8000",
        "http://pub0202.101.ru:8000",
        "http://pub0302.101.ru:8000",
    )
    output: list[Candidate] = []
    for channel_id, (title, page) in channels.items():
        alternatives = [
            f"{base}/stream/{tier}/{codec}/{bitrate}/{channel_id}"
            for tier, codec, bitrate in profiles
            for base in bases
        ]
        output.append(
            Candidate(
                site="101",
                name=title if title.startswith("101") else f"101.ru — {title}",
                url=alternatives[0],
                alternatives=alternatives[1:],
                source_page=page,
                discovered_by="101-template",
                codec_hint="AAC" if profiles[0][1] == "aac" else "MP3",
                bitrate_hint=profiles[0][2],
                metadata={"channel_id": channel_id},
            )
        )
    return output


def quality_bitrates(quality: str, preferred: int, available: Sequence[int]) -> list[int]:
    values = sorted(set(available))
    if quality == "low":
        return values
    if quality == "high":
        return list(reversed(values))
    # Auto: preferred first, then lower, then higher.
    return sorted(values, key=lambda x: (abs(x - preferred), x > preferred, x))


def radio_browser_matches_site(site: str, haystack: str) -> bool:
    checks = {
        "record": ("radio record", "radiorecord", "hostingradio.ru/rr_", "hostingradio.ru/deep"),
        "101": ("101.ru", ".101.ru/", "gpmradio.ru"),
        "zaycev": ("zaycev",),
        "relax": ("relax fm", "relax-fm.ru"),
        "caprice": ("radio caprice", "radcap"),
    }
    return any(token in haystack for token in checks[site])


def merge_candidates(candidates: Iterable[Candidate]) -> list[Candidate]:
    by_url: dict[str, Candidate] = {}
    for candidate in candidates:
        if not candidate.url:
            continue
        key = canonical_stream_url(candidate.url)
        current = by_url.get(key)
        if current is None:
            candidate.name = clean_title(candidate.name) or guess_name_from_url(candidate.url)
            candidate.alternatives = unique_preserve(candidate.alternatives)
            by_url[key] = candidate
            continue
        if len(candidate.name) > len(current.name) and not candidate.name.lower().startswith(("http", "www")):
            current.name = clean_title(candidate.name)
        current.alternatives = unique_preserve([*current.alternatives, *candidate.alternatives])
        if not current.source_page and candidate.source_page:
            current.source_page = candidate.source_page
        if candidate.discovered_by not in current.discovered_by:
            current.discovered_by += "+" + candidate.discovered_by
        current.metadata.update({k: v for k, v in candidate.metadata.items() if k not in current.metadata})
    return list(by_url.values())


def choose_best_per_station(streams: list[FinalStream]) -> list[FinalStream]:
    # Keep distinct URLs, but collapse obvious duplicates produced by templates and
    # Radio Browser for the same site/name. Prefer verified HTTPS and richer metadata.
    grouped: dict[tuple[str, str], list[FinalStream]] = {}
    for stream in streams:
        key = (stream.site.lower(), normalize_station_name(stream.name))
        grouped.setdefault(key, []).append(stream)
    output: list[FinalStream] = []
    for group in grouped.values():
        group.sort(key=final_stream_score, reverse=True)
        output.append(group[0])
        # Preserve additional verified streams only when their URLs are materially
        # different and the names are generic enough that they may be separate channels.
        if len(group) > 1 and normalize_station_name(group[0].name) in {"radio", "stream", "record"}:
            output.extend(group[1:])
    return output


def normalize_station_name(name: str) -> str:
    value = name.lower().replace("ё", "е")
    value = re.sub(r"\b(?:radio|радио|online|онлайн|fm)\b", " ", value)
    value = re.sub(r"[^a-zа-я0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip() or name.lower().strip()


def final_stream_score(stream: FinalStream) -> tuple[int, int, int, int, int]:
    return (
        1 if stream.ok else 0,
        1 if stream.url.startswith("https://") else 0,
        1 if stream.content_type.startswith("audio/") else 0,
        stream.bitrate_kbps,
        -len(stream.error),
    )


def probe_score(result: ProbeResult) -> tuple[int, int, int, int]:
    return (
        1 if result.ok else 0,
        1 if result.content_type.startswith("audio/") else 0,
        result.bytes_read,
        -len(result.error),
    )


def response_header_stream_hint(content_type: str) -> bool:
    return content_type in AUDIO_MIME_EXACT or content_type in PLAYLIST_MIMES


def detect_codec(content_type: str, body: bytes, url: str) -> str:
    mime = content_type.lower()
    if mime in PLAYLIST_MIMES:
        return "Playlist"
    if "mpegurl" in mime or urlsplit(url).path.lower().endswith((".m3u", ".m3u8")):
        return "Playlist"
    if "scpls" in mime or urlsplit(url).path.lower().endswith(".pls"):
        return "Playlist"
    if "mpeg" in mime and "video" not in mime:
        return "MP3"
    if "aac" in mime or "mp4a" in mime:
        return "AAC"
    if "ogg" in mime:
        if b"OpusHead" in body[:4096]:
            return "Opus"
        return "Ogg"
    if "flac" in mime:
        return "FLAC"
    if "wav" in mime or "wave" in mime:
        return "WAV"
    if mime == "video/mp2t":
        return "HLS/TS"

    sample = body[:8192]
    if sample.startswith(b"ID3"):
        return "MP3"
    if len(sample) >= 2 and sample[0] == 0xFF and (sample[1] & 0xE0) == 0xE0:
        # Could be MPEG audio or ADTS AAC. Layer bits 01 are invalid for MP3;
        # ADTS has 0xFFF sync and layer 00.
        if (sample[1] & 0x06) == 0:
            return "AAC"
        return "MP3"
    if sample.startswith(b"OggS"):
        return "Opus" if b"OpusHead" in sample else "Ogg"
    if sample.startswith(b"fLaC"):
        return "FLAC"
    if sample.startswith(b"RIFF") and sample[8:12] == b"WAVE":
        return "WAV"
    if len(sample) >= 564 and sample[0] == 0x47 and sample[188] == 0x47 and sample[376] == 0x47:
        return "HLS/TS"
    suffix = Path(urlsplit(url).path).suffix.lower()
    return AUDIO_EXTENSIONS.get(suffix, "Unknown")


def is_playlist_response(content_type: str, url: str, body: bytes) -> bool:
    path = urlsplit(url).path.lower()
    if content_type in PLAYLIST_MIMES or Path(path).suffix.lower() in PLAYLIST_EXTENSIONS:
        return True
    sample = body[:4096].lstrip().lower()
    return sample.startswith((b"#extm3u", b"[playlist]", b"<asx", b"<?xml")) and (
        b"http://" in sample or b"https://" in sample or b"#ext-x-" in sample
    )


def parse_playlist(body: bytes, base_url: str, content_type: str, quality: str) -> list[str]:
    text = body.decode("utf-8", errors="replace")
    if "�" in text[:200]:
        text = body.decode("latin-1", errors="replace")
    text = decode_embedded_text(text)
    entries: list[tuple[str, int]] = []

    if text.lstrip().upper().startswith("#EXTM3U"):
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        pending_bandwidth = 0
        for line in lines:
            if line.upper().startswith("#EXT-X-STREAM-INF"):
                match = re.search(r"BANDWIDTH=(\d+)", line, re.I)
                pending_bandwidth = int(match.group(1)) if match else 0
            elif not line.startswith("#"):
                url = clean_joined_url(base_url, line)
                if url:
                    entries.append((url, pending_bandwidth))
                pending_bandwidth = 0
    elif text.lstrip().lower().startswith("[playlist]"):
        for match in re.finditer(r"(?im)^File\d+\s*=\s*(.+?)\s*$", text):
            url = clean_joined_url(base_url, match.group(1).strip())
            if url:
                entries.append((url, 0))
    else:
        for match in re.finditer(r"(?i)(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", text):
            url = clean_joined_url(base_url, match.group(1))
            if url:
                entries.append((url, 0))
        if not entries:
            for match in URL_RE.finditer(text):
                url = clean_joined_url(base_url, match.group(0))
                if url:
                    entries.append((url, 0))

    deduped: dict[str, int] = {}
    for url, bandwidth in entries:
        deduped[url] = max(deduped.get(url, 0), bandwidth)
    values = list(deduped.items())
    if any(bw for _, bw in values):
        values.sort(key=lambda item: item[1], reverse=(quality == "high"))
    return [url for url, _ in values]


def unique_preserve(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if not value:
            continue
        key = canonical_stream_url(value)
        if key in seen:
            continue
        seen.add(key)
        output.append(value)
    return output


def intish(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_outputs(streams: list[FinalStream], out_dir: Path, include_unverified: bool) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    selected = [s for s in streams if s.ok or include_unverified]
    selected.sort(key=lambda s: (s.site.lower(), s.name.lower()))

    json_path = out_dir / "streams.json"
    report_path = out_dir / "streams_report.csv"
    m3u_path = out_dir / "playlist.m3u"
    yoradio_path = out_dir / "playlist.csv"

    json_path.write_text(
        json.dumps([asdict(s) for s in streams], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    fields = [
        "site", "name", "url", "ok", "status_code", "content_type", "codec",
        "bitrate_kbps", "bytes_read", "icy_name", "source_page", "discovered_by",
        "checked_at", "elapsed_ms", "error", "metadata",
    ]
    with report_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for stream in streams:
            row = asdict(stream)
            row["metadata"] = json.dumps(row["metadata"], ensure_ascii=False, separators=(",", ":"))
            writer.writerow(row)

    m3u_lines = ["#EXTM3U"]
    for stream in selected:
        attrs = []
        if stream.site:
            attrs.append(f'group-title="{m3u_escape(stream.site)}"')
        m3u_lines.append(f"#EXTINF:-1 {' '.join(attrs)},{m3u_escape(stream.name)}".rstrip())
        m3u_lines.append(stream.url)
    m3u_path.write_text("\n".join(m3u_lines) + "\n", encoding="utf-8")

    # yoRadio calls it CSV, but its native format is tab-separated and has no header.
    with yoradio_path.open("w", encoding="utf-8", newline="\n") as file:
        for stream in selected:
            name = stream.name.replace("\t", " ").replace("\r", " ").replace("\n", " ")
            url = stream.url.replace("\t", "").replace("\r", "").replace("\n", "")
            file.write(f"{name}\t{url}\t0\n")

    return {
        "json": json_path,
        "report": report_path,
        "m3u": m3u_path,
        "yoradio": yoradio_path,
    }


def m3u_escape(value: str) -> str:
    return value.replace("\r", " ").replace("\n", " ").replace('"', "'")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect and verify direct radio streams for Russian radio sites.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--sites",
        default="record,101,zaycev,relax,caprice",
        help="Comma-separated sites: record,101,zaycev,relax,caprice",
    )
    parser.add_argument("--out", type=Path, default=Path("radio_output"), help="Output directory")
    parser.add_argument("--verify", action=argparse.BooleanOptionalAction, default=True, help="Probe every stream")
    parser.add_argument(
        "--radio-browser",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use Radio Browser as a fallback source",
    )
    parser.add_argument(
        "--include-unverified",
        action="store_true",
        help="Include failed/unverified URLs in M3U and yoRadio playlist; report always contains all",
    )
    parser.add_argument("--quality", choices=("low", "auto", "high"), default="auto")
    parser.add_argument("--concurrency", type=int, default=12, help="Concurrent stream probes")
    parser.add_argument("--timeout", type=float, default=12.0, help="Per-request timeout in seconds")
    parser.add_argument("--delay", type=float, default=0.05, help="Minimum delay between HTTP requests")
    parser.add_argument("--probe-bytes", type=int, default=32768, help="Maximum bytes read from each stream")
    parser.add_argument("--playlist-depth", type=int, default=2, help="Maximum nested playlist depth")
    parser.add_argument("--max-playlist-entries", type=int, default=5)
    parser.add_argument("--max-pages", type=int, default=0, help="Override per-site page crawl limit; 0 uses defaults")
    parser.add_argument("--max-assets", type=int, default=0, help="Override per-site JS/JSON asset limit; 0 uses defaults")
    parser.add_argument("--max-text-bytes", type=int, default=4_000_000, help="Maximum text bytes read per page/asset")
    parser.add_argument("--max-101-channels", type=int, default=250, help="Maximum 101.ru channel IDs to resolve")
    parser.add_argument("--radio-browser-limit", type=int, default=1000)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification")
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.add_argument("--self-test", action="store_true", help="Run offline parser tests and exit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return parser


def validate_args(args: argparse.Namespace) -> list[str]:
    keys = [item.strip().lower() for item in args.sites.split(",") if item.strip()]
    invalid = sorted(set(keys) - set(SITE_SPECS))
    if invalid:
        raise SystemExit(f"Unknown site(s): {', '.join(invalid)}")
    if not keys:
        raise SystemExit("No sites selected")
    if args.concurrency < 1:
        raise SystemExit("--concurrency must be >= 1")
    if args.probe_bytes < 512:
        raise SystemExit("--probe-bytes must be >= 512")
    return unique_preserve(keys)


def run_self_test() -> None:
    sample = r'''
    <html><head><title>Test Radio</title></head><body>
    <script type="application/json">
      {"name":"Deep Test","streamUrl":"https:\/\/example.net\/stream\/aac\/64\/1"}
    </script>
    <audio src="https://example.net/live.mp3"></audio>
    </body></html>
    '''
    decoded = decode_embedded_text(sample)
    parser = PageParser()
    parser.feed(decoded)
    assert parser.title == "Test Radio"
    from_json = candidates_from_json_block(
        parser.json_blocks[0],
        base_url="https://example.org/",
        site="record",
        page_title=parser.title,
        source_page="https://example.org/",
        stream_hosts=("example.net",),
    )
    assert any(c.name == "Deep Test" and c.url == "https://example.net/stream/aac/64/1" for c in from_json)
    assert detect_codec("audio/mpeg", b"ID3\x04\x00", "https://x/live") == "MP3"
    assert detect_codec("audio/aac", b"\xff\xf1\x50\x80", "https://x/live") == "AAC"
    assert detect_codec("", b"OggS" + b"\x00" * 20 + b"OpusHead", "https://x/live") == "Opus"
    m3u = b"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=64000\nlow.m3u8\n#EXT-X-STREAM-INF:BANDWIDTH=256000\nhigh.m3u8\n"
    low = parse_playlist(m3u, "https://example.org/master.m3u8", "application/vnd.apple.mpegurl", "low")
    high = parse_playlist(m3u, "https://example.org/master.m3u8", "application/vnd.apple.mpegurl", "high")
    assert low[0].endswith("low.m3u8")
    assert high[0].endswith("high.m3u8")
    assert looks_like_stream("http://79.120.39.202:8000/dubtechno", ("radcap.ru",))
    print("Self-test passed")


async def async_main(args: argparse.Namespace, site_keys: list[str]) -> int:
    collector = StreamCollector(args)
    try:
        streams = await collector.run(site_keys)
    finally:
        await collector.close()

    paths = write_outputs(streams, args.out, args.include_unverified)
    ok_count = sum(1 for stream in streams if stream.ok)
    failed_count = len(streams) - ok_count
    print(f"Collected: {len(streams)}")
    print(f"Verified working: {ok_count}")
    print(f"Failed/unverified: {failed_count}")
    for label, path in paths.items():
        print(f"{label}: {path.resolve()}")
    return 0 if ok_count or not args.verify else 2


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    site_keys = validate_args(args)
    level = logging.WARNING
    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")
    try:
        return asyncio.run(async_main(args, site_keys))
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130
    except (httpx.HTTPError, socket.error, ssl.SSLError) as exc:
        logging.getLogger("radio-stream-collector").error("Network error: %s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
