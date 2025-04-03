# app/routers/cardio.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import supabase

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/cardio/{phone}", response_class=HTMLResponse)
async def cardio_page(request: Request, phone: str):
    return templates.TemplateResponse("cardio.html", {"request": request, "phone": phone})

@router.post("/cardio")
async def process_cardio(phone: str = Form(...),
                         max_hr: int = Form(...),
                         resting_hr: int = Form(...)):
    # 카르보넨 공식으로 목표 심박수 계산
    target60 = round((max_hr - resting_hr) * 0.6 + resting_hr)
    target70 = round((max_hr - resting_hr) * 0.7 + resting_hr)
    target80 = round((max_hr - resting_hr) * 0.8 + resting_hr)
    target90 = round((max_hr - resting_hr) * 0.9 + resting_hr)

    # 계산된 데이터를 Supabase의 cardio_evaluations 테이블에 저장
    supabase.table("cardio_evaluations").insert({
        "phone": phone,
        "max_hr": max_hr,
        "resting_hr": resting_hr,
        "target_60": target60,
        "target_70": target70,
        "target_80": target80,
        "target_90": target90
    }).execute()

    return RedirectResponse(url=f"/member/{phone}", status_code=302)
