import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from app.routers import auth, user, dashboard, member, journal, routine, body, cardio, pain

load_dotenv()

app = FastAPI()
secret_key = os.getenv("SECRET_KEY")  # .env 파일에서 SECRET_KEY 가져오기
app.add_middleware(SessionMiddleware, secret_key=secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(dashboard.router)
app.include_router(member.router)
app.include_router(journal.router)
app.include_router(routine.router)
app.include_router(body.router)
app.include_router(cardio.router)
app.include_router(pain.router)

@app.get("/")
async def root():
    return {"message": "GPT Rehab AI 프로젝트에 오신 것을 환영합니다!"}
