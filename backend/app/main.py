from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from supabase_auth.types import User

from app.auth.dependencies import get_current_user
from app.config import settings

app = FastAPI(title="Document Copilot")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/auth/me")
async def get_me(user: Annotated[User, Depends(get_current_user)]) -> dict[str, Any]:
    return {"id": user.id, "email": user.email}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)

