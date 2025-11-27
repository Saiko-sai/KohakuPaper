"""
Paper data downloader from papercopilot/paperlists repository
"""

import json
import re
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from .config import (
    PAPERLISTS_RAW_URL,
    PAPERLISTS_API_URL,
    DATA_DIR,
    CACHE_DIR,
    CONFERENCES,
)


def fetch_json(url: str, timeout: int = 30) -> dict | list | None:
    """Fetch JSON from URL"""
    try:
        req = Request(url, headers={"User-Agent": "KohakuPaper/0.4.0"})
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError) as e:
        print(f"Error fetching {url}: {e}")
        return None


def list_conference_files(conference: str) -> list[str]:
    """List available JSON files for a conference from GitHub API"""
    url = f"{PAPERLISTS_API_URL}/{conference}"
    data = fetch_json(url)
    if not data:
        return []

    files = []
    for item in data:
        if item.get("type") == "file" and item.get("name", "").endswith(".json"):
            files.append(item["name"])
    return sorted(files)


def parse_year_from_filename(filename: str) -> int | None:
    """Extract year from filename like 'iclr2024.json' or 'nips2024.json'"""
    match = re.search(r"(\d{4})", filename)
    if match:
        return int(match.group(1))
    return None


def download_paper_list(
    conference: str,
    year: int | None = None,
    force: bool = False,
) -> Path | None:
    """
    Download paper list JSON for a conference/year.
    Returns path to downloaded file or None on failure.
    """
    conference = conference.lower()
    if conference not in CONFERENCES:
        print(f"Unknown conference: {conference}")
        return None

    # Determine filename
    if year:
        filename = f"{conference}{year}.json"
    else:
        # Get latest available
        files = list_conference_files(conference)
        if not files:
            print(f"No files found for {conference}")
            return None
        filename = files[-1]  # Latest by sort order
        year = parse_year_from_filename(filename)

    # Check if already exists
    target_path = DATA_DIR / filename
    if target_path.exists() and not force:
        print(f"File already exists: {target_path}")
        return target_path

    # Download
    url = f"{PAPERLISTS_RAW_URL}/{conference}/{filename}"
    print(f"Downloading {url}...")

    data = fetch_json(url, timeout=120)
    if data is None:
        return None

    # Save to file
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    print(f"Saved to {target_path} ({len(data)} papers)")
    return target_path


def download_all_for_conference(
    conference: str,
    min_year: int | None = None,
    max_year: int | None = None,
    force: bool = False,
) -> list[Path]:
    """Download all available years for a conference"""
    conference = conference.lower()
    files = list_conference_files(conference)
    downloaded = []

    for filename in files:
        year = parse_year_from_filename(filename)
        if year is None:
            continue
        if min_year and year < min_year:
            continue
        if max_year and year > max_year:
            continue

        path = download_paper_list(conference, year, force=force)
        if path:
            downloaded.append(path)

    return downloaded


def list_local_files() -> list[Path]:
    """List all downloaded JSON files in data directory"""
    return sorted(DATA_DIR.glob("*.json"))


def get_available_conferences() -> dict[str, list[int]]:
    """Get dict of conferences to available years from local files"""
    result: dict[str, list[int]] = {}

    for path in list_local_files():
        filename = path.stem
        # Extract conference and year from filename like 'iclr2024'
        match = re.match(r"([a-z]+)(\d{4})", filename)
        if match:
            conf = match.group(1)
            year = int(match.group(2))
            if conf not in result:
                result[conf] = []
            result[conf].append(year)

    for conf in result:
        result[conf].sort()

    return result
