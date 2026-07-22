import httpx
import logging
from config import load_settings

logger = logging.getLogger("api_server.ollama")
settings = load_settings()

async def check_ollama_status() -> bool:
    """Check if Ollama server is running and reachable."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(settings.OLLAMA_HOST)
            if response.status_code == 200:
                return True
            return False
    except (httpx.ConnectError, httpx.TimeoutException, Exception) as e:
        logger.error(f"Ollama health check failed: {e}")
        return False

async def is_model_available(model_name: str) -> bool:
    """Check if a specific model is loaded in Ollama."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_HOST}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name") for m in data.get("models", [])]
                return any(model_name in name for name in models)
            return False
    except Exception as e:
        logger.error(f"Error checking model availability: {e}")
        return False

async def pull_model(model_name: str) -> bool:
    """Pull the model from Ollama registry. Warning: This can take time depending on model size."""
    logger.info(f"Pulling model {model_name}... This may take a while.")
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            # We use a very long timeout because model downloads can be large
            response = await client.post(
                f"{settings.OLLAMA_HOST}/api/pull",
                json={"name": model_name, "stream": False}
            )
            if response.status_code == 200:
                logger.info(f"Successfully pulled model {model_name}.")
                return True
            else:
                logger.error(f"Failed to pull model: {response.text}")
                return False
    except Exception as e:
        logger.error(f"Error pulling model {model_name}: {e}")
        return False

async def ensure_ollama_ready() -> dict:
    """
    Ensure Ollama is running and the required model is available.
    Returns a status dict.
    """
    status = {
        "running": False,
        "model_loaded": False,
        "message": ""
    }
    
    if not await check_ollama_status():
        status["message"] = "Ollama is not running. Please start Ollama."
        return status
        
    status["running"] = True
    
    if not await is_model_available(settings.OLLAMA_MODEL):
        logger.info(f"Model {settings.OLLAMA_MODEL} not found. Attempting to pull...")
        success = await pull_model(settings.OLLAMA_MODEL)
        if not success:
            status["message"] = f"Failed to automatically pull model {settings.OLLAMA_MODEL}. Please run 'ollama pull {settings.OLLAMA_MODEL}' manually."
            return status
            
    status["model_loaded"] = True
    status["message"] = "Ollama and model are ready."
    return status
