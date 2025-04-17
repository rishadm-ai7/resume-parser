from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import uuid
import requests
import json

router = APIRouter(prefix="/resume", tags=["Resume"])


class Resume(BaseModel):
    name: str
    skills: List[str]
    certifications: List[str]
    tools: List[str]


@router.post("/")
def add_resume(resume: Resume):

    doc_id = str(uuid.uuid4())
    doc = resume.dict()

    # Define the Elasticsearch endpoint
    es_url = f"http://elasticsearch:9200/resumes/_doc/{doc_id}"

    # Set the appropriate headers
    headers = {"Content-Type": "application/json"}

    # Send the request to Elasticsearch
    response = requests.put(es_url, headers=headers, data=json.dumps(doc))

    # Check for errors
    if response.status_code not in [200, 201]:

        return {"error": response.json()}

    return {"status": "inserted", "id": doc_id, "data": resume}
