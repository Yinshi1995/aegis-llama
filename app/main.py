from fastapi import FastAPI, Request
from fastapi.responses import Response
import gradio as gr
import httpx
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

app = FastAPI()


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_ollama(request: Request, path: str):
    """Proxy all /api/* requests to Ollama."""
    url = f"{OLLAMA_BASE_URL}/api/{path}"
    body = await request.body()
    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
        resp = await client.request(
            method=request.method,
            url=url,
            content=body,
            headers={"content-type": request.headers.get("content-type", "application/json")},
        )
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type"),
    )


def create_gradio_app():
    with gr.Blocks(title="Aegis") as demo:
        gr.Markdown("# Aegis Agent")
        gr.Markdown("System is running.")
        gr.Markdown(f"**Ollama endpoint:** `{OLLAMA_BASE_URL}`")
    return demo


gradio_app = create_gradio_app()
app = gr.mount_gradio_app(app, gradio_app, path="/ui")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
