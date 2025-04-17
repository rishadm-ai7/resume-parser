from fastapi import APIRouter, Query
import requests
import json

router = APIRouter(prefix="/delete_resume", tags=["Resume"])


@router.delete("/")
def delete_resume(user_id: str = Query(None), name: str = Query(None)):
    if not user_id and not name:
        return {"error": "At least one of 'user_id' or 'name' must be provided."}

    es_url = "http://elasticsearch:9200/resumes/_delete_by_query"
    headers = {"Content-Type": "application/json"}

    must_clauses = []
    if user_id:
        must_clauses.append({"term": {"user_id.keyword": user_id}})
    if name:
        must_clauses.append({"term": {"name.keyword": name}})

    query = {"query": {"bool": {"must": must_clauses}}}

    response = requests.post(es_url, headers=headers, data=json.dumps(query))

    if response.status_code != 200:
        return {"error": response.json()}

    return {"status": "deleted", "details": response.json()}
