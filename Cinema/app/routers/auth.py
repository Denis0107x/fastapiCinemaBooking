from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.core.security import verify_password, create_access_token

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    error = None
    user = crud.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        error = "Неверная электронная почта или пароль"
    else:
        token_data  = {"email": user.email}
        token = create_access_token(token_data)
        response = RedirectResponse(url="/profile", status_code=303)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response 
    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response
