"""
Ollama AI Service
Integrates with local Ollama instance for AI-powered explanations
"""

import asyncio
import httpx
import json
from typing import Dict, Optional
from app.core.config import settings


class OllamaService:
    """
    Service for interacting with local Ollama instance
    
    Features:
    - Configurable endpoint and model
    - Timeout handling
    - Retry logic with exponential backoff
    - Structured JSON response parsing
    - Graceful error handling
    """
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.enabled = settings.OLLAMA_ENABLED
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    async def generate_explanation(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        """
        Generate AI explanation using Ollama
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instructions
            temperature: Randomness (0.0-1.0, lower = more focused)
            max_tokens: Maximum response length
            
        Returns:
            dict with 'success', 'explanation', and optional 'error'
        """
        # Check if Ollama is enabled
        if not self.enabled:
            return {
                'success': False,
                'explanation': 'AI explanations are currently disabled.',
                'error': 'OLLAMA_DISABLED'
            }
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                return await self._make_request(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            except Exception as e:
                # If last attempt, return error
                if attempt == self.max_retries - 1:
                    return {
                        'success': False,
                        'explanation': 'Unable to generate AI explanation at this time.',
                        'error': str(e)
                    }
                
                # Wait before retry with exponential backoff (non-blocking)
                wait_time = self.retry_delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
        
        return {
            'success': False,
            'explanation': 'AI service unavailable after multiple attempts.',
            'error': 'MAX_RETRIES_EXCEEDED'
        }
    
    async def _make_request(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Dict:
        """Make HTTP request to Ollama API"""
        
        # Construct the full prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        # Make request to Ollama API
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            # Check response status
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract explanation text
            explanation = result.get('response', '').strip()
            
            if not explanation:
                raise ValueError("Empty response from Ollama")
            
            return {
                'success': True,
                'explanation': explanation,
                'model': self.model,
                'tokens': result.get('eval_count', 0)
            }
    
    async def generate_structured_explanation(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3  # Lower for more consistent structured output
    ) -> Dict:
        """
        Generate structured explanation (attempts to return JSON)
        
        This method instructs the model to return structured data
        but falls back to text if parsing fails.
        
        Args:
            prompt: The user prompt (should request JSON format)
            system_prompt: Optional system instructions
            temperature: Randomness (lower for structured data)
            
        Returns:
            dict with 'success', 'data' (structured), and optional 'error'
        """
        result = await self.generate_explanation(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=1500
        )
        
        if not result['success']:
            return result
        
        # Try to parse as JSON
        explanation = result['explanation']
        
        # Try to extract JSON from markdown code blocks
        if '```json' in explanation:
            try:
                json_start = explanation.index('```json') + 7
                json_end = explanation.index('```', json_start)
                json_str = explanation[json_start:json_end].strip()
                parsed_data = json.loads(json_str)
                
                return {
                    'success': True,
                    'data': parsed_data,
                    'raw_explanation': explanation,
                    'model': result.get('model')
                }
            except (ValueError, json.JSONDecodeError):
                pass
        
        # Try to parse the entire response as JSON
        try:
            parsed_data = json.loads(explanation)
            return {
                'success': True,
                'data': parsed_data,
                'raw_explanation': explanation,
                'model': result.get('model')
            }
        except json.JSONDecodeError:
            # Return as text if JSON parsing fails
            return {
                'success': True,
                'data': {'explanation': explanation},
                'raw_explanation': explanation,
                'model': result.get('model'),
                'note': 'Response was not in JSON format'
            }
    
    async def check_health(self) -> Dict:
        """
        Check if Ollama service is available
        
        Returns:
            dict with 'available', 'model', and optional 'error'
        """
        if not self.enabled:
            return {
                'available': False,
                'error': 'Ollama is disabled in configuration'
            }
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Check if Ollama is running
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                # Check if our model is available
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                
                model_available = any(self.model in m for m in models)
                
                return {
                    'available': True,
                    'ollama_running': True,
                    'model_available': model_available,
                    'model': self.model,
                    'available_models': models
                }
        except Exception as e:
            return {
                'available': False,
                'ollama_running': False,
                'error': str(e)
            }


# Create singleton instance
ollama_service = OllamaService()
