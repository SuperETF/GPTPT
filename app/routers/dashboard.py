# app/routers/dashboard.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import supabase

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def trainer_dashboard(request: Request):
    trainer_id = request.session.get("trainer_id")
    if not trainer_id:
        return RedirectResponse(url="/login", status_code=302)
    
    result = supabase.table("members").select("*").eq("trainer_id", trainer_id).execute()
    members = result.data
    return templates.TemplateResponse("dashboard.html", {"request": request, "members": members})
