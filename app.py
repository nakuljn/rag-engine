#!/usr/bin/env python3

import os
import sys
import threading
import time
import logging
import uvicorn
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_fastapi_server():
    try:
        logger.info("Starting FastAPI backend server on port 8000...")
        from main import app

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )

    except Exception as e:
        logger.error(f"Failed to start FastAPI server: {e}")
        raise

def wait_for_api_server(max_retries=20, delay=4):
    import requests

    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                logger.info("✅ FastAPI server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass

        logger.info(f"⏳ Waiting for FastAPI server... ({i+1}/{max_retries})")
        time.sleep(delay)

    logger.error("❌ FastAPI server failed to start within timeout")
    return False

def create_gradio_app():
    try:
        from gradio_ui import RAGGradioUI
        ui = RAGGradioUI()
        demo = ui.create_interface()
        return demo

    except Exception as e:
        logger.error(f"Failed to create Gradio app: {e}")
        raise

def main():
    logger.info("🚀 Starting RAG Engine Application...")
    try:
        logger.info("Starting FastAPI backend thread...")
        api_thread = threading.Thread(
            target=start_fastapi_server,
            daemon=True,
            name="FastAPI-Server"
        )
        api_thread.start()

        logger.info("Waiting for backend to be ready...")
        if not wait_for_api_server():
            logger.error("Backend server failed to start. Exiting.")
            sys.exit(1)

        logger.info("Creating Gradio frontend...")
        demo = create_gradio_app()

        logger.info("🎉 Launching Gradio UI on port 7860...")
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=False,
            show_error=True,
            show_api=False,
            favicon_path=None,
            ssl_verify=False,
            quiet=False,
            inbrowser=False
        )

    except KeyboardInterrupt:
        logger.info("👋 Shutting down RAG Engine...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()