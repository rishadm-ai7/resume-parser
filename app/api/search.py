from fastapi import APIRouter
import requests
import json

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
def fuzzy_search(q: str):
    es_url = "http://elasticsearch:9200/resumes/_search"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    query = {
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["skills", "tools", "certifications"],
                "fuzziness": "AUTO",
            }
        }
    }

    response = requests.get(es_url, headers=headers, data=json.dumps(query))

    if response.status_code != 200:
        return {"error": response.json()}

    hits = response.json().get("hits", {}).get("hits", [])
    return {"results": [hit["_source"] for hit in hits]}
