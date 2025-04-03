import logging
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import openai
import os
from app.db import supabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# OpenAI API 키 설정 (.env 파일에서 로드)
openai.api_key = os.getenv("OPENAI_API_KEY")

def build_routine_prompt(phone: str) -> str:
    """
    Supabase에서 회원 정보, 체성분, 통증, 운동 일지, 피드백 데이터를 조회하여
    운동 루틴 생성을 위한 프롬프트를 생성합니다.
    """
    member_data = supabase.table("members").select("*").eq("phone", phone).execute().data
    body_data = supabase.table("body_compositions").select("*").eq("phone", phone).order("created_at", desc=True).execute().data
    pain_data = supabase.table("pain_levels").select("*").eq("phone", phone).order("created_at", desc=True).execute().data
    journal_data = supabase.table("journals").select("*").eq("phone", phone).order("created_at", desc=True).execute().data
    feedback_data = supabase.table("routine_feedbacks").select("*").eq("phone", phone).order("created_at", desc=True).execute().data

    # 필수 데이터가 없으면 빈 문자열 반환 (루틴 생성 불가)
    if not member_data or not body_data:
        return ""
    
    member = member_data[0]
    body = body_data[0]
    pain = pain_data[0] if pain_data else {}
    journal = journal_data[0] if journal_data else {}
    feedback = feedback_data[0] if feedback_data else {}

    prompt = f"""
    회원 정보:
    이름: {member.get('name', '정보 없음')}
    전화번호: {phone}

    체성분:
    체중: {body.get('weight', '정보 없음')} kg
    체지방률: {body.get('body_fat', '정보 없음')} %
    근육량: {body.get('muscle_mass', '정보 없음')} kg

    통증 정보:
    NRS: {pain.get('nrs', '정보 없음')}
    통증 부위: {pain.get('pain_area', '정보 없음')}

    최근 운동 일지:
    {journal.get('content', '정보 없음')}

    최근 피드백:
    트레이너: {feedback.get('trainer_feedback', '없음')}
    회원: {feedback.get('member_feedback', '없음')}

    회원의 운동 목표는 체지방 감소와 근력 향상입니다.
    위 정보를 바탕으로, 회원에게 최적의 운동 루틴을 제안해 주세요.
    """
    return prompt.strip()


@router.post("/routine")
async def create_routine(request: Request, phone: str = Form(...)):
    """
    POST /routine 엔드포인트:
    1. Supabase에서 필요한 데이터를 조회하여 프롬프트를 생성합니다.
    2. OpenAI API를 호출해 운동 루틴을 생성합니다.
    3. 생성된 운동 루틴을 Supabase의 routines 테이블에 저장합니다.
    4. 저장 후, 회원의 운동 일지 페이지(/journal-calendar/{phone})로 리디렉션합니다.
    """
    prompt = build_routine_prompt(phone)
    if not prompt:
        raise HTTPException(status_code=400, detail="루틴 생성을 위한 데이터가 부족합니다.")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 전문 피트니스 트레이너입니다. 아래 정보를 참고하여 운동 루틴을 제안해 주세요."
                },
                {"role": "user", "content": prompt}
            ]
        )
        routine_text = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("OpenAI API 호출 오류: %s", str(e))
        raise HTTPException(status_code=500, detail=f"운동 루틴 생성 중 오류 발생: {str(e)}")
    
    result = supabase.table("routines").insert({
        "phone": phone,
        "prompt": prompt,
        "routine_text": routine_text
    }).execute()
    
    if not result.data:
        logger.error("Supabase INSERT 오류: 데이터가 반환되지 않음. 반환값: %s", result)
        raise HTTPException(status_code=500, detail="운동 루틴 저장 중 오류가 발생했습니다.")
    
    logger.info("운동 루틴 저장 성공: %s", result.data)
    
    # POST 후, 회원의 운동 일지 페이지로 리디렉션
    return RedirectResponse(url=f"/journal-calendar/{phone}", status_code=302)
