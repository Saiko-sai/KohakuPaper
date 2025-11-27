"""
Data management endpoints
"""

from fastapi import APIRouter

from ...config import CONFERENCES
from ...downloader import (
    download_paper_list,
    download_all_for_conference,
    list_local_files,
    list_conference_files,
)
from ...database import get_available_data

router = APIRouter()


@router.get("/conferences")
async def list_conferences():
    """List all supported conferences"""
    return {
        "conferences": CONFERENCES,
        "local": get_available_data(),
    }


@router.get("/conferences/{conference}/files")
async def list_conference_json_files(conference: str):
    """List available JSON files for a conference on GitHub"""
    files = list_conference_files(conference.lower())
    return {"conference": conference, "files": files}


@router.get("/local-files")
async def list_local_json_files():
    """List downloaded JSON files"""
    files = list_local_files()
    return {"files": [{"name": f.name, "size": f.stat().st_size} for f in files]}


@router.post("/download/{conference}")
async def download_conference_data(
    conference: str,
    year: int | None = None,
    force: bool = False,
):
    """Download paper data for a conference (JSON files only, no import needed)"""
    if year:
        path = download_paper_list(conference, year, force=force)
        if path:
            return {"status": "success", "file": path.name}
        return {"status": "error", "message": "Download failed"}
    else:
        paths = download_all_for_conference(conference, force=force)
        if paths:
            return {
                "status": "success",
                "files": [p.name for p in paths],
            }
        return {"status": "error", "message": "No files downloaded"}
