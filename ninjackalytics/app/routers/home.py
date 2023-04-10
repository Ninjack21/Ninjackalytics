from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="frontend/templates/home")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/opponent_scout", response_class=HTMLResponse)
async def opponent_scout(request: Request):
    return templates.TemplateResponse("opponent_scout.html", {"request": request})


@router.get("/user_account", response_class=HTMLResponse)
async def user_account(request: Request):
    return templates.TemplateResponse("user_account.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
