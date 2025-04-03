# app/routers/member.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import supabase

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 회원 등록 페이지 (트레이너가 자신의 회원을 등록할 때)
@router.get("/register-member", response_class=HTMLResponse)
async def register_member_page(request: Request):
    if "trainer_id" not in request.session:
        return RedirectResponse(url="/login", status_code=302)
    # 템플릿 폴더 구조에 따라 "member/register_member.html"과 같이 수정할 수 있습니다.
    return templates.TemplateResponse("register_member.html", {"request": request})

# 회원 등록 (휴대폰 번호를 식별자로 사용)
@router.post("/register-member")
async def register_member(request: Request, name: str = Form(...), phone: str = Form(...)):
    trainer_id = request.session.get("trainer_id")
    if not trainer_id:
        return {"error": "로그인이 필요합니다."}
    
    # 이미 등록된 전화번호인지 확인
    existing = supabase.table("members").select("phone").eq("phone", phone).execute().data
    if existing:
        return {"error": f"이미 등록된 전화번호입니다: {phone}"}
    
    supabase.table("members").insert({
        "name": name,
        "phone": phone,
        "trainer_id": trainer_id
    }).execute()
    return RedirectResponse(url="/dashboard", status_code=302)

# 회원 상세 페이지 (URL: /member/{phone})
@router.get("/member/{phone}", response_class=HTMLResponse)
async def member_detail(request: Request, phone: str):
    member_data = supabase.table("members").select("*").eq("phone", phone).execute().data
    if not member_data:
        return RedirectResponse(url="/dashboard", status_code=302)
    member = member_data[0]
    # 템플릿 파일 경로는 "member/member_detail.html" 등으로 구성할 수 있습니다.
    return templates.TemplateResponse("member_detail.html", {"request": request, "member": member})

# 통증 입력 (휴대폰 번호를 식별자로 사용)
@router.post("/member/{phone}/pain")
async def record_pain(phone: str, nrs: int = Form(...), pain_area: str = Form(...)):
    supabase.table("pain_levels").insert({
        "phone": phone,
        "nrs": nrs,
        "pain_area": pain_area
    }).execute()
    return RedirectResponse(url=f"/member/{phone}", status_code=302)

# 체형 불균형 평가 (휴대폰 번호를 식별자로 사용)
@router.post("/member/{phone}/posture")
async def record_posture(phone: str, imbalance: str = Form(...)):
    supabase.table("posture_assessments").insert({
        "phone": phone,
        "imbalance": imbalance
    }).execute()
    return RedirectResponse(url=f"/member/{phone}", status_code=302)
