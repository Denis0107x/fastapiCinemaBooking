from fastapi import APIRouter, Depends, HTTPException, Request, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.security import decode_token
from app.database import get_db
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/movies/{movie_id}/reviews", response_model=schemas.Review)
async def create_review(
    request: Request,
    movie_id: int,
    text: str = Form(...),  # Принимаем текст отзыва из формы
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                movie = crud.get_movie(db, movie_id)
                if not movie:
                    raise HTTPException(status_code=404, detail="Movie not found")
                
                review = schemas.ReviewCreate(text=text)  # Создаем объект ReviewCreate
                db_review = crud.create_review(db=db, review=review, user_id=userdata.id, movie_id=movie_id)
                return RedirectResponse(url=f"/movies/{movie_id}", status_code=303)
    return RedirectResponse(url="/registration", status_code=303)