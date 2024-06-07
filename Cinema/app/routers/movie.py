from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile, Cookie, Query
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.core.security import decode_token
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import shutil

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/movies", response_class=HTMLResponse)
async def read_movies(
    request: Request, 
    title: str = Query(None), 
    country: str = Query(None), 
    genre: str = Query(None), 
    year: str = Query(None), 
    premiere_date: str = Query(None), 
    access_token: str = Cookie(default=None), 
    db: Session = Depends(get_db)
):
    movies = crud.search_movies(db, title=title, country=country, genre=genre, year=year, premiere_date=premiere_date)
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                params = {"request": request, "current_user": token_data, "username": userdata.username, "movies": movies}
                return templates.TemplateResponse("movies.html", params)
    return templates.TemplateResponse("movies.html", {"request": request, "movies": movies})

@router.get("/movies/{movie_id}", response_class=HTMLResponse)
async def read_movie(request: Request, movie_id: int, access_token: str = Cookie(default=None), db: Session = Depends(get_db)):
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                movie = crud.get_movie(db, movie_id=movie_id)
                if movie is None:
                     raise HTTPException(status_code=404, detail="Movie not found")
                reviews = crud.get_reviews_for_movie(db, movie_id)
                params = {"request": request, "current_user": token_data, "username":userdata.username, "movie": movie, "reviews": reviews}
                return templates.TemplateResponse("movie_detail.html", params)
    movie = crud.get_movie(db, movie_id=movie_id)
    reviews = crud.get_reviews_for_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return templates.TemplateResponse("movie_detail.html", {"request": request, "movie": movie, "reviews": reviews})

@router.get("/create_movie", response_class=HTMLResponse)
async def create_movie_form(request: Request, access_token: str = Cookie(default=None),  db: Session = Depends(get_db)):
     if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                if userdata.username != "admin":
                     raise HTTPException(status_code=403, detail="У вас нет прав на создание фильма")
                    

                return templates.TemplateResponse("create_movie.html", {"request": request, "current_user": token_data, "username": userdata.username })
   

@router.post("/movies/", response_class=HTMLResponse)
async def create_movie(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    poster: UploadFile = File(...),
    country: str = Form(...),
    genre: str = Form(...),
    director: str = Form(...),
    year: int = Form(...),
    premiere_date: str = Form(...),
    duration: int = Form(...),
    rating: float = Form(...),
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    poster_filename = poster.filename
    poster_path = f"app/static/posters/{poster_filename}"
    with open(poster_path, "wb") as buffer:
        shutil.copyfileobj(poster.file, buffer)
    
    poster_url = f"/posters/{poster_filename}"

    movie_data = schemas.MovieCreate(
        title=title,
        description=description,
        poster=poster_url,
        country=country,
        genre=genre,
        director=director,
        year=year,
        premiere_date=premiere_date,
        duration=duration,
        rating=rating
    )
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                if userdata.username != "admin":
                     raise HTTPException(status_code=403, detail="У вас нет прав на создание фильма")
                    
                crud.create_movie(db=db, movie=movie_data)
                return templates.TemplateResponse("create_movie.html", {"request": request, "current_user": token_data, "username": userdata.username })

@router.get("/api/movies", response_class=JSONResponse)
async def search_movies(
    title: str = Query(None),
    country: str = Query(None),
    genre: str = Query(None),
    year: str = Query(None),
    premiere_date: str = Query(None),
    db: Session = Depends(get_db)
):
    year_int = int(year) if year else None
    movies = crud.search_movies(db, title=title, country=country, genre=genre, year=year_int, premiere_date=premiere_date)
    return movies

@router.get("/chat/{movie_id}", response_class=HTMLResponse)
async def get_chat(request: Request, movie_id: int, access_token: str = Cookie(default=None), db: Session = Depends(get_db)):
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                movie = crud.get_movie(db, movie_id=movie_id)
                if movie is None:
                    raise HTTPException(status_code=404, detail="Movie not found")
                messages = crud.get_messages(db, movie_id=movie_id)
                params = {"request": request, "current_user": token_data, "username": userdata.username, "movie": movie, "messages": messages}
                return templates.TemplateResponse("chat.html", params)
    return templates.TemplateResponse("registration.html", {"request": request, "messages": []})

