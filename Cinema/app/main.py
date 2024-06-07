from fastapi import FastAPI, Request, Cookie, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app import models, crud
from app.routers import user, auth, movie, booking, review, chat
from app.database import engine, get_db
from app.core.config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/posters", StaticFiles(directory="app/static/posters"), name="posters")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request, access_token: str = Cookie(default=None), db: Session = Depends(get_db)):
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                params = {"request": request, "current_user": token_data, "username": userdata.username}
                return templates.TemplateResponse("index.html", params)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request, access_token: str = Cookie(default=None), db: Session = Depends(get_db)):
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                params = {"request": request, "current_user": token_data, "username": userdata.username}
                return templates.TemplateResponse("about.html", params)
    return templates.TemplateResponse("about.html", {"request": request})


app.include_router(user.router)
app.include_router(auth.router)
app.include_router(movie.router)
app.include_router(booking.router)
app.include_router(review.router)
app.include_router(chat.router)
