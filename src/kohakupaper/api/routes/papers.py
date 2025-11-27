"""
Paper query endpoints
"""

from fastapi import APIRouter, Query

from ...database import (
    query_papers,
    count_papers,
    get_available_filters,
    get_available_data,
    clean_records,
)

router = APIRouter()


@router.get("")
async def list_papers(
    conference: str | None = Query(
        None, description="Conference name (e.g., iclr, nips)"
    ),
    year: int | None = Query(None, description="Specific year"),
    status: str | None = Query(None, description="Paper status (Accept, Reject, etc.)"),
    primary_area: str | None = Query(None, description="Primary research area"),
    search: str | None = Query(None, description="Search in title, abstract, keywords"),
    min_rating: float | None = Query(None, description="Minimum average rating"),
    max_rating: float | None = Query(None, description="Maximum average rating"),
    min_confidence: float | None = Query(
        None, description="Minimum average confidence"
    ),
    max_confidence: float | None = Query(
        None, description="Maximum average confidence"
    ),
    has_rating_diff: bool | None = Query(
        None, description="Filter papers with rating diff"
    ),
    has_confidence_diff: bool | None = Query(
        None, description="Filter papers with confidence diff"
    ),
    title_filter: str | None = Query(None, description="Filter by title substring"),
    limit: int = Query(50, ge=1, le=500, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    order_by: str = Query("rating_avg", description="Sort field"),
    order_dir: str = Query("DESC", description="Sort direction (ASC/DESC)"),
):
    """List papers with filters and pagination"""
    papers = query_papers(
        conference=conference,
        year=year,
        status=status,
        primary_area=primary_area,
        search=search,
        min_rating=min_rating,
        max_rating=max_rating,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        has_rating_diff=has_rating_diff,
        has_confidence_diff=has_confidence_diff,
        title_filter=title_filter,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_dir=order_dir,
    )

    total = count_papers(
        conference=conference,
        year=year,
        status=status,
        primary_area=primary_area,
        search=search,
        min_rating=min_rating,
        max_rating=max_rating,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        has_rating_diff=has_rating_diff,
        has_confidence_diff=has_confidence_diff,
        title_filter=title_filter,
    )

    return {
        "papers": clean_records(papers),
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/filters")
async def get_filters(
    conference: str | None = Query(None),
    year: int | None = Query(None),
):
    """Get available filter options for given conference/year"""
    filters = get_available_filters(conference=conference, year=year)
    # Also include available conferences and years
    available = get_available_data()
    return {
        **filters,
        "conferences": list(available.keys()),
        "years_by_conference": available,
    }
