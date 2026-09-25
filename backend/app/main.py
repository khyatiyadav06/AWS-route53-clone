import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, SessionLocal, engine
from app.models import *
from app.routes import auth, hosted_zones, records
from app.services.seed import seed

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed(db)

app = FastAPI(title="Route 53 Clone API", version="2.0.0", description="Mock AWS Route 53 management console API")
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(hosted_zones.router)
app.include_router(records.router)

@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "route53-clone-api", "version": "2.0.0"}
