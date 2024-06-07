from fastapi import APIRouter, Depends, HTTPException, Request, Form, Cookie
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.core.security import  decode_token
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/registration", response_class=HTMLResponse)
async def registration_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})

@router.post("/users/", response_model=schemas.User)
async def create_user(request: Request, username: str = Form(...), email: str = Form(...), phone_number: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    error = None
    db_user = crud.get_user_by_email(db, email=email)
    
    if db_user:
        error = "Аккаунт с таким email уже зарегистрирован"
    elif crud.get_user_by_phone_number(db, phone_number=phone_number):
        error = "Аккаунт с таким номером телефона уже зарегистрирован"
    elif password != confirm_password:
        error = "Пароли не совпадают"
    elif len(password) < 6:
        error = "Пароль должен содержать не менее 6 символов"
    else:
        db_user, token = crud.create_user(db=db, user=schemas.UserCreate(username=username, email=email, phone_number=phone_number, password=password))
    
        # Устанавливаем токен в cookie и выполняем редирект
        response = RedirectResponse(url="/success_registration", status_code=303)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
        
    return templates.TemplateResponse("registration.html", {"request": request, "error": error})
    

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, access_token: str = Cookie(None), db: Session = Depends(get_db)):
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                bookings = crud.get_bookings_for_user(db, userdata.id)
                for booking in bookings:
                    movie = crud.get_movie(db, booking.movie_id)
                    booking.movie_title = movie.title
                    booking.row = (booking.seat_number - 1) // 25 + 1
                    booking.seat = (booking.seat_number - 1) % 25 + 1
                params = {
                    "request": request,
                    "current_user": token_data,
                    "username": userdata.username,
                    "email": userdata.email,
                    "phone_number": userdata.phone_number,
                    "bookings": bookings
                }
                return templates.TemplateResponse("profile.html", params)
    return RedirectResponse(url="/login")


@router.post("/pay", response_class=HTMLResponse)
async def pay_booking(
    request: Request,
    booking_id: int = Form(...),
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                booking = crud.get_booking_by_id(db, booking_id)
                if not booking or booking.user_id != userdata.id:
                    raise HTTPException(status_code=404, detail="Booking not found or you do not have permission to pay for this booking")

                # Фиктивный процесс оплаты

                # Обновляем статус бронирования
                crud.update_booking_payment_status(db, booking_id, True)

                return RedirectResponse("/profile", status_code=303)

    return RedirectResponse(url="/login")


@router.get("/success_registration", response_class=HTMLResponse)
async def success_registration_page(request: Request, access_token: str = Cookie(None)):
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("username")
            return templates.TemplateResponse("success_registration.html", {"request": request, "current_user": token_data, "username": username})
    
    # Если нет доступа, перенаправляем на страницу входа
    return RedirectResponse(url="/login")



