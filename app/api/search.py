from fastapi import APIRouter, Query
import requests
import json

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
def fuzzy_search(q: str = Query(default=None)):
    es_url = "http://elasticsearch:9200/resumes/_search"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    if q:
        query = {
            "query": {
                "multi_match": {
                    "query": q,
                    "fields": ["tools/technologies", "skillset", "certifications"],
                    "fuzziness": "AUTO",
                }
            }
        }
    else:
        query = {"query": {"match_all": {}}}

    response = requests.get(es_url, headers=headers, data=json.dumps(query))

    if response.status_code != 200:
        return {"error": response.json()}

    hits = response.json().get("hits", {}).get("hits", [])
    return {"results": [hit["_source"] for hit in hits]}
