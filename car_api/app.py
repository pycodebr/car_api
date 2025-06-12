from fastapi import FastAPI

from car_api.routers import router as car_router

app = FastAPI()
app.include_router(car_router)
