"""
FastAPI Application Entry Point
Main application configuration and routing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, profile, risk, portfolio, sip, market, recommendation, portfolio_analysis, diversification_analysis, monte_carlo, ollama_health


# Lifespan event handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler
    - Startup: Create database tables
    - Shutdown: Clean up resources
    """
    # Startup
    print("🚀 Starting application...")
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("✅ Database tables created successfully!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down application...")


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
app.include_router(portfolio.router, prefix=f"{settings.API_V1_PREFIX}/portfolio", tags=["Portfolio"])
app.include_router(portfolio_analysis.router, prefix=f"{settings.API_V1_PREFIX}/portfolio-analysis", tags=["Portfolio Analysis"])
app.include_router(diversification_analysis.router, prefix=f"{settings.API_V1_PREFIX}/diversification-analysis", tags=["Diversification Analysis"])
app.include_router(monte_carlo.router, prefix=f"{settings.API_V1_PREFIX}/monte-carlo", tags=["Monte Carlo Simulation"])
app.include_router(sip.router, prefix=f"{settings.API_V1_PREFIX}/sip", tags=["SIP Plans"])
app.include_router(market.router, prefix=f"{settings.API_V1_PREFIX}/market", tags=["Market Data"])
app.include_router(ollama_health.router, prefix=f"{settings.API_V1_PREFIX}/ollama", tags=["AI Service"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
