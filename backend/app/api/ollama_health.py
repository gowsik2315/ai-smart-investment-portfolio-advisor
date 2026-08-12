"""
Ollama Health Check API
Endpoint for checking Ollama service availability
"""

from fastapi import APIRouter
from app.services.ollama_service import ollama_service

router = APIRouter()


@router.get("/health")
async def check_ollama_health():
    """
    Check Ollama service health and availability
    
    Returns:
        dict with Ollama status information
    """
    health = await ollama_service.check_health()
    
    return {
        "status": "available" if health.get("available") else "unavailable",
        "details": health
    }


@router.get("/test")
async def test_ollama_generation():
    """
    Test Ollama generation with a simple prompt
    
    Returns:
        dict with test result
    """
    result = await ollama_service.generate_explanation(
        prompt="Explain the concept of investment diversification in one sentence.",
        temperature=0.7
    )
    
    return {
        "test_status": "success" if result["success"] else "failed",
        "result": result
    }
