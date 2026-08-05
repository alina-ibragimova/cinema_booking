from fastapi import FastAPI

from src.api.routers import auth_router, bookings_router, halls_router, movies_router, showtime_router


app = FastAPI(title="Cinema Booking API",
    description="Асинхронный API для бронирования билетов в кино",
    version="1.0.0")


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(bookings_router)
app.include_router(auth_router)
app.include_router(halls_router)
app.include_router(showtimes_router)
app.include_router(bookings_router)
 
@app.get("/", tags=["Check"])
async def root():
    return {"status": "ok", "message": "Cinema API is running"}