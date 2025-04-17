from fastapi import FastAPI
from app.api import resume_parser, search, delete_user, flush_es_db

app = FastAPI()


app.include_router(resume_parser.router)
app.include_router(search.router)
app.include_router(delete_user.router)
app.include_router(flush_es_db.router)
