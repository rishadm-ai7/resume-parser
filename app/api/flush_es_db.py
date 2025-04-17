from fastapi import APIRouter
import requests
import json

router = APIRouter(prefix="/flush_resumes", tags=["Flush all Data"])


@router.delete("/all")
def delete_all_resumes():
    es_url = "http://elasticsearch:9200/resumes/_delete_by_query"
    headers = {"Content-Type": "application/json"}

    query = {"query": {"match_all": {}}}

    response = requests.post(es_url, headers=headers, data=json.dumps(query))

    if response.status_code != 200:
        return {"error": response.json()}

    return {"status": "all documents deleted", "details": response.json()}
