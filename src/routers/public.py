"""
Public router for FastAPI
Handles public endpoints and pages
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Home page
    """
    # Starlette 0.35+ expects the Request as the first argument
    return templates.TemplateResponse(request, "index.html", {"request": request})
