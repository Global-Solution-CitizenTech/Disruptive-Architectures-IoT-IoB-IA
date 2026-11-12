"""
Ponto de Entrada Padrão ASGI (`uvicorn main:app`) — ZelaFix AI
Compatível com Render Cloud e execução local via `python main.py` ou `uvicorn main:app`.
"""
import os
import uvicorn
from api import app
from src.core.config import PORT

__all__ = ["app"]

if __name__ == "__main__":
    reload_ativo = os.environ.get("UVICORN_RELOAD", "false").lower() == "true"
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=reload_ativo)
