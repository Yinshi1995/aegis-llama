from fastapi import FastAPI, Request
from fastapi.responses import Response, StreamingResponse, JSONResponse
import httpx
import logging
import os
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aegis")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

app = FastAPI()


@app.get("/")
async def root():
    """Root health endpoint."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            models = resp.json().get("models", [])
            model_names = [m.get("name") for m in models]
        return {"status": "ok", "ollama": "connected", "models": model_names}
    except Exception as e:
        return {"status": "ok", "ollama": f"error: {e}", "models": []}


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_ollama(request: Request, path: str):
    """Proxy all /api/* requests to Ollama with streaming support."""
    url = f"{OLLAMA_BASE_URL}/api/{path}"
    body = await request.body()
    logger.info(f"Proxying {request.method} /api/{path} -> {url}")
    start = time.time()

    try:
        client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0))
        req = client.build_request(
            method=request.method,
            url=url,
            content=body,
            headers={"content-type": request.headers.get("content-type", "application/json")},
        )
        resp = await client.send(req, stream=True)

        async def stream_response():
            try:
                async for chunk in resp.aiter_bytes(1024):
                    yield chunk
            finally:
                await resp.aclose()
                await client.aclose()
                elapsed = time.time() - start
                logger.info(f"Completed /api/{path} in {elapsed:.1f}s")

        return StreamingResponse(
            stream_response(),
            status_code=resp.status_code,
            media_type=resp.headers.get("content-type", "application/json"),
        )
    except httpx.TimeoutException:
        logger.error(f"Timeout proxying /api/{path} after {time.time() - start:.1f}s")
        await client.aclose()
        return JSONResponse({"error": "Ollama request timed out"}, status_code=504)
    except Exception as e:
        logger.error(f"Error proxying /api/{path}: {e}")
        try:
            await client.aclose()
        except Exception:
            pass
        return JSONResponse({"error": str(e)}, status_code=502)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
