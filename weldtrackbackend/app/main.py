import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.api import router
from app.db import Base, engine, SessionLocal

Base.metadata.create_all(bind=engine)

ENV = os.getenv("ENV", "development")
IS_PROD = ENV == "production"

app = FastAPI(
    title="Weldtrack",
    root_path="/api",
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    openapi_url=None if IS_PROD else "/openapi.json"
)

origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "name": "weldtrack",
        "status": "online"
    }

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
