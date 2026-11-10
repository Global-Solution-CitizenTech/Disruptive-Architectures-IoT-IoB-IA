"""
Aplicação Principal FastAPI - ZelaFix IA, IoT & IoB Engine
FIAP Global Solution 2026/2 - CitizenTech
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from ..config import PROJECT_NAME, PROJECT_VERSION, DEBUG
from .routes import router

def create_app() -> FastAPI:
    """Fábrica de inicialização da aplicação FastAPI."""
    app = FastAPI(
        title=PROJECT_NAME,
        version=PROJECT_VERSION,
        description=(
            "Plataforma de Inteligência Artificial Multimodal, RAG Normativo, "
            "Telemetria IoT e Análise Comportamental (IoB) para Zeladoria Urbana Colaborativa. "
            "Alinhada à ODS 11 da ONU na FIAP Global Solution 2026/2."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        debug=DEBUG
    )

    # Configuração de CORS para permitir requisições do Expo Mobile e Frontend Web
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inclusão das rotas da API
    app.include_router(router)

    # Montagem de arquivos estáticos para o Dashboard da Banca
    static_dir = Path(__file__).resolve().parent.parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", include_in_schema=False)
    def root_redirect():
        return RedirectResponse(url="/dashboard")

    @app.get("/dashboard", include_in_schema=False)
    def dashboard_redirect():
        from fastapi.responses import FileResponse
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return RedirectResponse(url="/docs")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    from ..config import APP_HOST, APP_PORT
    uvicorn.run("src.api.app:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)

