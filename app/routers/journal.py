import logging
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from app.db import supabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/journal")
async def create_journal(
    request: Request,
    phone: str = Form(...),
    entry_date: str = Form(...),
    content: str = Form(...)
):
    """
    운동 일지를 새로 작성하는 POST 요청을 처리하고,
    작성 후 /journal-calendar/{phone}로 리디렉션합니다.
    """
    try:
        entry_date_obj = datetime.strptime(entry_date, "%Y-%m-%d").date()
    except ValueError:
        logger.error("잘못된 날짜 형식: %s", entry_date)
        raise HTTPException(
            status_code=400,
            detail="유효하지 않은 날짜 형식입니다. YYYY-MM-DD 형식이어야 합니다."
        )

    insert_data = {
        "phone": phone,
        "entry_date": str(entry_date_obj),
        "content": content
    }

    # Supabase에 데이터 INSERT
    result = supabase.table("journals").insert(insert_data).execute()

    # 결과 데이터가 없으면 INSERT 실패로 간주
    if not result.data:
        logger.error("Supabase INSERT 오류: 데이터가 반환되지 않음. 반환값: %s", result)
        raise HTTPException(
            status_code=500,
            detail="운동 일지를 저장하는 중 오류가 발생했습니다."
        )

    logger.info("운동 일지 저장 성공: %s", result.data)

    # POST 요청 후, GET 라우트(/journal-calendar/{phone})로 리디렉션
    return RedirectResponse(url=f"/journal-calendar/{phone}", status_code=302)


@router.get("/journal-calendar/{phone}", response_class=HTMLResponse)
async def get_journal_calendar(request: Request, phone: str):
    """
    /journal-calendar/{phone} 경로로 GET 요청이 들어왔을 때,
    해당 회원(phone)의 운동 일지와 루틴 정보를 조회하여
    journal_calendar.html 템플릿으로 보여줍니다.
    """
    journals_result = supabase.table("journals") \
        .select("*") \
        .eq("phone", phone) \
        .order("created_at", desc=True) \
        .execute()

    routines_result = supabase.table("routines") \
        .select("*") \
        .eq("phone", phone) \
        .order("created_at", desc=True) \
        .execute()

    # 데이터가 없으면 빈 리스트로 처리 (회원이 아직 작성하지 않았을 수 있으므로)
    journals = journals_result.data if journals_result.data is not None else []
    routines = routines_result.data if routines_result.data is not None else []
    latest_routine = routines[0] if routines else None

    return templates.TemplateResponse("journal_calendar.html", {
        "request": request,
        "phone": phone,
        "journals": journals,
        "routine": latest_routine
    })
