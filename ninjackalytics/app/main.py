from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import home

app = FastAPI()

# Mount the static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include the different routes
app.include_router(home.router)
