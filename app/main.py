from fastapi import FastAPI
from app.api import resume_parser, search

app = FastAPI()


app.include_router(resume_parser.router)
app.include_router(search.router)
