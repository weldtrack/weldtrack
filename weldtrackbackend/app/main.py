import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


load_dotenv()

from app.api import router
from app.db import Base, engine, SessionLocal


Base.metadata.create_all(bind=engine)

from app.bootstrap.admin import create_initial_admin


# Run one-time admin bootstrap if appropriate
create_initial_admin()

app = FastAPI(title="Weldtrack")
origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
