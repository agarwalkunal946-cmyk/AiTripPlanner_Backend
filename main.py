from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from routes import auth_routes, trip_routes, ai_routes, chat_routes, payment_routes
from services.socket_manager import sio
import socketio
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Trip Planner API",
    description="An advanced API for creating, sharing, and planning trips with AI assistance.",
    version="2.0.0"
)

socket_app = socketio.ASGIApp(sio)
app.mount('/socket.io', socket_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred."},
    )

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(trip_routes.router, prefix="/trips", tags=["Trips"])
app.include_router(ai_routes.router, prefix="/ai", tags=["AI Planner"])
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])
app.include_router(payment_routes.router, prefix="/payments", tags=["Payments"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Trip Planner API", "status": "running"}