"""
FastAPI Application Entry Point
Main application configuration and routing
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import (
    auth,
    users,
    profile,
    risk,
    sip,
    market,
    recommendation,
    portfolio,
    portfolio_analysis,
    diversification_analysis,
    monte_carlo,
    ml,
    ollama_health,
)


logger = logging.getLogger("app.startup")


# Lifespan event handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler
    - Startup: Create database tables
    - Shutdown: Clean up resources

    Startup messages go through `logging` and contain only ASCII. The
    previous emoji `print()` calls raised UnicodeEncodeError and aborted
    startup on Windows whenever stdout was not UTF-8 — which is the case
    any time output is redirected to a file or the app runs as a service
    rather than in an interactive terminal.
    """
    # Startup
    logger.info("Starting application...")

    # The placeholder secret is published in .env.example, so tokens
    # signed with it can be forged by anyone. Refuse to serve with it
    # outside development rather than silently issuing forgeable tokens.
    if settings.is_placeholder_secret:
        if settings.DEBUG:
            logger.warning(
                "SECRET_KEY is the placeholder from .env.example. JWTs signed "
                "with it can be forged. Set a real one before deploying: "
                "python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        else:
            raise RuntimeError(
                "SECRET_KEY is still the placeholder from .env.example and DEBUG "
                "is off. Refusing to start: tokens signed with a published key "
                "can be forged by anyone. Generate one with "
                "python -c \"import secrets; print(secrets.token_hex(32))\""
            )

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine, checkfirst=True)
    logger.info("Database tables ready.")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Smart Investment Portfolio Advisor API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Smart Investment Portfolio Advisor API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(profile.router, prefix=f"{settings.API_V1_PREFIX}/profile", tags=["Profile"])
app.include_router(risk.router, prefix=f"{settings.API_V1_PREFIX}/risk", tags=["Risk Assessment"])
app.include_router(recommendation.router, prefix=f"{settings.API_V1_PREFIX}/recommendation", tags=["Portfolio Recommendation"])
app.include_router(portfolio.router, prefix=f"{settings.API_V1_PREFIX}/portfolio", tags=["Portfolio Tracking"])
app.include_router(portfolio_analysis.router, prefix=f"{settings.API_V1_PREFIX}/portfolio-analysis", tags=["Portfolio Analysis"])
app.include_router(diversification_analysis.router, prefix=f"{settings.API_V1_PREFIX}/diversification-analysis", tags=["Diversification Analysis"])
app.include_router(monte_carlo.router, prefix=f"{settings.API_V1_PREFIX}/monte-carlo", tags=["Monte Carlo Simulation"])
app.include_router(sip.router, prefix=f"{settings.API_V1_PREFIX}/sip", tags=["SIP Plans"])
app.include_router(market.router, prefix=f"{settings.API_V1_PREFIX}/market", tags=["Market Data"])

# ML-based volatility forecasting. Kept on its own tag, distinct from the
# Ollama-backed "AI Service" below: one is a trained model producing a
# number, the other is an LLM producing prose.
app.include_router(ml.router, prefix=f"{settings.API_V1_PREFIX}/ml", tags=["ML Volatility Forecasting"])

app.include_router(ollama_health.router, prefix=f"{settings.API_V1_PREFIX}/ollama", tags=["AI Explanations"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
