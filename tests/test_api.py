"""
Test the API endpoints using httpx client.
Run the server first: kohakupaper serve
Then run this script: python tests/test_api.py
"""

import httpx

BASE_URL = "http://127.0.0.1:48891"


def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    r = httpx.get(f"{BASE_URL}/api/health")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    print("  OK!\n")


def test_conferences():
    """Test conferences listing"""
    print("Testing /api/data/conferences...")
    r = httpx.get(f"{BASE_URL}/api/data/conferences")
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  Supported conferences: {len(data['conferences'])}")
    print(f"  Local data: {data['local']}")
    print("  OK!\n")


def test_local_files():
    """Test local files listing"""
    print("Testing /api/data/local-files...")
    r = httpx.get(f"{BASE_URL}/api/data/local-files")
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  Files: {[f['name'] for f in data['files']]}")
    print("  OK!\n")


def test_filters():
    """Test filters endpoint"""
    print("Testing /api/papers/filters...")
    r = httpx.get(f"{BASE_URL}/api/papers/filters")
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  Conferences: {data.get('conferences', [])}")
    print(f"  Statuses: {data.get('statuses', [])}")
    print(f"  Areas count: {len(data.get('primary_areas', []))}")
    print("  OK!\n")


def test_papers_list():
    """Test papers listing"""
    print("Testing /api/papers (list papers)...")
    r = httpx.get(f"{BASE_URL}/api/papers", params={"limit": 5})
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  Total papers: {data['total']}")
    print(f"  Returned: {len(data['papers'])}")
    if data["papers"]:
        p = data["papers"][0]
        print(f"  First paper: {p.get('title', 'N/A')[:60]}...")
        print(f"    Rating: {p.get('rating_avg')}")
        print(f"    Status: {p.get('status')}")
    print("  OK!\n")


def test_papers_search():
    """Test papers search"""
    print("Testing /api/papers with search='transformer'...")
    r = httpx.get(
        f"{BASE_URL}/api/papers", params={"search": "transformer", "limit": 3}
    )
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  Total matches: {data['total']}")
    for p in data["papers"]:
        print(f"    - {p.get('title', 'N/A')[:60]}...")
    print("  OK!\n")


def test_papers_filter_status():
    """Test papers filtered by status"""
    print("Testing /api/papers with status='Oral'...")
    r = httpx.get(f"{BASE_URL}/api/papers", params={"status": "Oral", "limit": 3})
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  Total Oral papers: {data['total']}")
    for p in data["papers"]:
        print(f"    [{p.get('rating_avg', 'N/A')}] {p.get('title', 'N/A')[:50]}...")
    print("  OK!\n")


def test_statistics_summary():
    """Test statistics summary"""
    print("Testing /api/statistics/summary...")
    r = httpx.get(f"{BASE_URL}/api/statistics/summary")
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  Total papers: {data.get('total_papers')}")
    print(f"  Avg rating: {data.get('avg_rating')}")
    print(f"  Accepted: {data.get('accepted_count')}")
    print(f"  Rejected: {data.get('rejected_count')}")
    print("  OK!\n")


def test_statistics_by_status():
    """Test statistics by status"""
    print("Testing /api/statistics/by-status...")
    r = httpx.get(f"{BASE_URL}/api/statistics/by-status")
    print(f"  Status: {r.status_code}")
    data = r.json()
    for row in data[:5]:
        print(
            f"    {row.get('status')}: {row.get('paper_count')} papers, avg rating: {row.get('avg_rating'):.2f}"
            if row.get("avg_rating")
            else f"    {row.get('status')}: {row.get('paper_count')} papers"
        )
    print("  OK!\n")


def test_rating_distribution():
    """Test rating distribution"""
    print("Testing /api/statistics/rating-distribution...")
    r = httpx.get(f"{BASE_URL}/api/statistics/rating-distribution", params={"bins": 10})
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  Bins: {len(data.get('bins', []))}")
    print(f"  Total counts: {sum(data.get('counts', []))}")
    print("  OK!\n")


def test_yearly_stats():
    """Test yearly statistics"""
    print("Testing /api/statistics/yearly...")
    r = httpx.get(f"{BASE_URL}/api/statistics/yearly")
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  Years covered: {len(data)}")
    for row in data[:3]:
        print(
            f"    {row.get('conference')} {row.get('year')}: {row.get('paper_count')} papers"
        )
    print("  OK!\n")


def test_top_areas():
    """Test top areas"""
    print("Testing /api/statistics/top-areas...")
    r = httpx.get(f"{BASE_URL}/api/statistics/top-areas", params={"limit": 5})
    print(f"  Status: {r.status_code}")
    data = r.json()
    for row in data:
        print(
            f"    {row.get('primary_area', 'N/A')[:40]}: {row.get('paper_count')} papers"
        )
    print("  OK!\n")


def main():
    print("=" * 60)
    print("KohakuPaper API Test")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}\n")

    try:
        test_health()
        test_conferences()
        test_local_files()
        test_filters()
        test_papers_list()
        test_papers_search()
        test_papers_filter_status()
        test_statistics_summary()
        test_statistics_by_status()
        test_rating_distribution()
        test_yearly_stats()
        test_top_areas()

        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
    except httpx.ConnectError:
        print("ERROR: Could not connect to server.")
        print("Make sure the server is running: kohakupaper serve")
    except AssertionError as e:
        print(f"ASSERTION ERROR: {e}")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
