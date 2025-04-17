from fastapi import FastAPI
from app.api import resume_parser, search, delete_user

app = FastAPI()


app.include_router(resume_parser.router)
app.include_router(search.router)
app.include_router(delete_user.router)
