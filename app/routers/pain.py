# app/routers/pain.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import supabase

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# GET: 통증 입력 전용 페이지 (URL: /pain-level/{phone})
@router.get("/pain-level/{phone}", response_class=HTMLResponse)
async def pain_level_page(request: Request, phone: str):
    # 템플릿에 phone을 전달하여 해당 회원의 통증 입력 페이지를 표시합니다.
    return templates.TemplateResponse("pain_level.html", {"request": request, "phone": phone})

# POST: 통증 입력 데이터를 DB에 저장한 후 회원 상세 페이지로 리디렉션
@router.post("/pain-level")
async def submit_pain_level(
    phone: str = Form(...),
    nrs: int = Form(...),
    pain_area: str = Form(...)
):
    supabase.table("pain_levels").insert({
        "phone": phone,
        "nrs": nrs,
        "pain_area": pain_area
    }).execute()
    return RedirectResponse(url=f"/member/{phone}", status_code=302)
