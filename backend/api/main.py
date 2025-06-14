from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routes import companies, documents, analysis
from .auth import auth_router, get_current_user
from .middleware.logging import LoggingMiddleware
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="EULA Comparison API",
    description="API for analyzing and comparing Terms of Service and EULAs",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(
    companies.router,
    prefix="/companies",
    tags=["Companies"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["Analysis"],
    dependencies=[Depends(get_current_user)]
)