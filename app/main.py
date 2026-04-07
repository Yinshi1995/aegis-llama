import gradio as gr
import os


def create_app():
    with gr.Blocks(title="Aegis") as app:
        gr.Markdown("# Aegis Agent")
        gr.Markdown("System is running. Add your interface here.")

        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        gr.Markdown(f"**Ollama endpoint:** `{ollama_url}`")

    return app


if __name__ == "__main__":
    port = int(os.getenv("GRADIO_SERVER_PORT", os.getenv("PORT", "7860")))
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=port)
