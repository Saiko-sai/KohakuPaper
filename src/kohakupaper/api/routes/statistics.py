"""
Statistics and analytics endpoints
"""

from fastapi import APIRouter, Query

from ...database import (
    get_statistics,
    get_rating_distribution,
    get_yearly_stats,
    get_connection,
    build_json_source,
    clean_dict,
    clean_records,
)

router = APIRouter()


@router.get("/summary")
async def get_summary(
    conference: str | None = Query(None),
    year: int | None = Query(None),
):
    """Get overall summary statistics"""
    json_source = build_json_source(conference, year)
    if not json_source:
        return {
            "total_papers": 0,
            "avg_rating": None,
            "std_rating": None,
            "min_rating": None,
            "max_rating": None,
            "accepted_count": 0,
            "rejected_count": 0,
        }

    conn = get_connection()

    query = f"""
        SELECT
            COUNT(*) as total_papers,
            AVG(rating_avg[1]) as avg_rating,
            STDDEV(rating_avg[1]) as std_rating,
            MIN(rating_avg[1]) as min_rating,
            MAX(rating_avg[1]) as max_rating,
            AVG(confidence_avg[1]) as avg_confidence,
            SUM(gs_citation) FILTER (WHERE gs_citation >= 0) as total_citations,
            AVG(gs_citation) FILTER (WHERE gs_citation >= 0) as avg_citations,
            COUNT(*) FILTER (WHERE status IN ('Accept', 'Oral', 'Spotlight', 'Poster')) as accepted_count,
            COUNT(*) FILTER (WHERE status IN ('Reject', 'Withdrawn', 'Withdraw')) as rejected_count
        FROM read_json({json_source}, auto_detect=true, format='array')
    """

    try:
        result = conn.execute(query).fetchdf()
        conn.close()
        return clean_dict(result.to_dict(orient="records")[0])
    except Exception as e:
        conn.close()
        return {"error": str(e)}


@router.get("/by-status")
async def stats_by_status(
    conference: str | None = Query(None),
    year: int | None = Query(None),
):
    """Get statistics grouped by status"""
    return clean_records(
        get_statistics(conference=conference, year=year, group_by="status")
    )


@router.get("/by-area")
async def stats_by_area(
    conference: str | None = Query(None),
    year: int | None = Query(None),
):
    """Get statistics grouped by primary area"""
    return clean_records(
        get_statistics(conference=conference, year=year, group_by="primary_area")
    )


@router.get("/by-track")
async def stats_by_track(
    conference: str | None = Query(None),
    year: int | None = Query(None),
):
    """Get statistics grouped by track"""
    return clean_records(
        get_statistics(conference=conference, year=year, group_by="track")
    )


@router.get("/rating-distribution")
async def rating_distribution(
    conference: str | None = Query(None),
    year: int | None = Query(None),
    step: float = Query(0.1, ge=0.05, le=2.0),
    primary_area: str | None = Query(None, description="Filter by primary area"),
):
    """Get rating distribution for histogram

    Args:
        step: Bin width (e.g., 0.1 for 6.0-6.1, 0.5 for 6.0-6.5, 1.0 for 6-7)
        primary_area: Filter by primary area (partial match)
    """
    return get_rating_distribution(
        conference=conference, year=year, step=step, primary_area=primary_area
    )


@router.get("/yearly")
async def yearly_stats(
    conference: str | None = Query(None),
):
    """Get statistics grouped by year (across multiple JSON files)"""
    return clean_records(get_yearly_stats(conference=conference))


@router.get("/top-areas")
async def top_areas(
    conference: str | None = Query(None),
    year: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """Get top primary areas by paper count"""
    json_source = build_json_source(conference, year)
    if not json_source:
        return []

    conn = get_connection()

    query = f"""
        SELECT
            primary_area,
            COUNT(*) as paper_count,
            AVG(rating_avg[1]) as avg_rating,
            COUNT(*) FILTER (WHERE status IN ('Accept', 'Oral', 'Spotlight', 'Poster')) as accepted_count
        FROM read_json({json_source}, auto_detect=true, format='array')
        WHERE primary_area IS NOT NULL AND primary_area != ''
        GROUP BY primary_area
        ORDER BY paper_count DESC
        LIMIT {limit}
    """

    try:
        result = conn.execute(query).fetchdf()
        conn.close()
        return clean_records(result.to_dict(orient="records"))
    except Exception as e:
        conn.close()
        return {"error": str(e)}
