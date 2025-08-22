from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .templates import templates
from .routers import auth, hub, questionnaire_api, random_api

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- CORS origins robust parsing ---
origins = []
if settings.EMBED_ALLOWED_ORIGINS:
    origins = [o.strip() for o in settings.EMBED_ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],  # dev: minden engedett; PROD-ban állíts pontos listát!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.templates = templates

app.include_router(auth.router)
app.include_router(hub.router)
app.include_router(random_api.router)
app.include_router(questionnaire_api.router)