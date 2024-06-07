from fastapi import APIRouter, Depends, HTTPException, Request, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.security import decode_token
from app.database import get_db
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/movies/{movie_id}/booking", response_class=HTMLResponse)
async def choose_seat(
    request: Request,
    movie_id: int,
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
                # Получаем список доступных мест для бронирования
                booked_seats = crud.get_booked_seats(db, movie_id)
                total_seats = 250
                available_seats = [seat for seat in range(1, total_seats+1) if seat not in booked_seats]

                params = {"request": request, "movie": movie, "available_seats": available_seats, "current_user": token_data, "username": userdata.username,  "booked_seats": booked_seats}
                return templates.TemplateResponse("booking.html", params)

    
    return templates.TemplateResponse("index.html", {"request": request, "message": "Unauthorized"})

@router.post("/movies/{movie_id}/booking", response_class=HTMLResponse)
async def book_seat(
    request: Request,
    movie_id: int,
    seat_number: int = Form(...),  # Получаем номер места из формы
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
                
                # Получаем список забронированных мест для фильма
                booked_seats = crud.get_booked_seats(db, movie_id)
                
                # Проверяем, что выбранное место доступно для бронирования
                if seat_number in booked_seats:
                    raise HTTPException(status_code=400, detail="Selected seat is not available for booking")
                
                # Создаем запись о бронировании в базе данных
                crud.create_booking(db=db, user_id=userdata.id, movie_id=movie_id, seat_number=seat_number)
                
                # Перенаправляем пользователя на страницу подтверждения бронирования
                return RedirectResponse("/profile", status_code=303)
    
    raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/pay", response_class=HTMLResponse)
async def pay_booking(
    request: Request,
    booking_id: int = Form(...),
    card_number: str = Form(...),
    expiration_date: str = Form(...),
    cvv: str = Form(...),
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
                # Здесь вы можете добавить проверки и логику для обработки оплаты

                # Обновляем статус бронирования
                crud.update_booking_payment_status(db, booking_id, True)

                return RedirectResponse("/profile", status_code=303)

    return RedirectResponse(url="/login")

@router.get("/pay/{booking_id}", response_class=HTMLResponse)
async def payment_form(request: Request, booking_id: int, access_token: str = Cookie(default=None), db: Session = Depends(get_db)):
    if access_token:
        token_data = decode_token(access_token)
        if token_data:
            username = token_data.get("email")
            userdata = crud.get_user_by_email(db=db, email=username)
            if userdata:
                booking = crud.get_booking_by_id(db, booking_id)
                if not booking or booking.user_id != userdata.id:
                    raise HTTPException(status_code=404, detail="Booking not found or you do not have permission to pay for this booking")
                params = {"request": request, "booking_id": booking_id, "current_user":token_data, "username": userdata.username}
                return templates.TemplateResponse("payment_form.html", params )

    return RedirectResponse(url="/login")

