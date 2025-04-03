# app/routers/user.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import supabase

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/register-user", response_class=HTMLResponse)
async def register_user_page(request: Request):
    return templates.TemplateResponse("register_user.html", {"request": request})

@router.post("/register-user")
async def register_user(request: Request, email: str = Form(...), password: str = Form(...)):
    result = supabase.table("users").insert({
        "email": email,
        "password": password  # 실제 운영 시에는 비밀번호 해시화 필요
    }).execute()
    return RedirectResponse(url="/login", status_code=302)
