import os



from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.lifespan import lifespan

from dotenv import load_dotenv
load_dotenv()

from app.core.logging import get_logger
logger = get_logger("app")

app = FastAPI(
    title="FastAPI + SQLAlchemy 2.0 CRUD",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,    
    lifespan=lifespan,
    redirect_slashes=False
)

logger.info(f'Инициализация приложения',DEBUG=settings.DEBUG, APP_ENV=settings.APP_ENV)

# if settings.DEBUG:
#     logger.info(f'Режим DEBUG add_middleware')
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=["*"],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )
# else:
#     logger.info(f'НЕ режим DEBUG')

app.include_router(api_router, prefix="/backend/v1")

from fastapi import FastAPI, Depends

@app.get("/health")
async def health_check():  
    return {"status": "ok"}
