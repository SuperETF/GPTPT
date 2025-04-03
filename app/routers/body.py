# app/routers/body.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import supabase

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 체성분 입력 페이지 (회원 식별: phone 사용)
@router.get("/body-composition/{phone}", response_class=HTMLResponse)
async def body_composition_page(request: Request, phone: str):
    return templates.TemplateResponse("body_composition.html", {"request": request, "phone": phone})

# 체성분 입력 처리
@router.post("/body-composition")
async def submit_body_composition(
    phone: str = Form(...),
    weight: float = Form(...),
    body_fat: float = Form(...),
    muscle_mass: float = Form(...)
):
    supabase.table("body_compositions").insert({
        "phone": phone,
        "weight": weight,
        "body_fat": body_fat,
        "muscle_mass": muscle_mass
    }).execute()
    return RedirectResponse(url=f"/member/{phone}", status_code=302)
