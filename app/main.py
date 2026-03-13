from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, auth, documents
from app.database import create_db_tables

security = HTTPBearer()

app = FastAPI(title="BrainAPI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db_tables()

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)

@app.get("/")
def root():
    return {"message": "BrainAPI is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}