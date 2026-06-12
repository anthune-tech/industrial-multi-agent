from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_data import router as data_router
from api.routes_agent import router as agent_router
from db.connection import init_db

app = FastAPI(title="Industrial Plant Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_router, prefix="/api/data", tags=["data"])
app.include_router(agent_router, prefix="/api/agent", tags=["agent"])


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/api/health")
async def health():
    return {"status": "ok"}
