from fastapi import APIRouter, HTTPException, Query
from services.ytdlp_service import search_videos

router = APIRouter()

@router.get("/")
def search(
    q: str = Query(..., description="検索ワード"),
    max_results: int = Query(10, le=50),
    sort: str = Query("relevance", enum=["relevance", "date", "viewCount"])
):
    try:
        results = search_videos(q, max_results, sort)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
