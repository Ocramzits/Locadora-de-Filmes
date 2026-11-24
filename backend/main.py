from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import filmes, clientes, locacoes, relatorios

app = FastAPI(
    title="Locadora de Filmes API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filmes.router)
app.include_router(clientes.router)
app.include_router(locacoes.router)
app.include_router(relatorios.router)

@app.on_event("startup")
def startup_event():
    try:
        from backend.seed import seed_database
        seed_database()
    except Exception as e:
        print(f"Aviso ao inicializar/popular banco de dados: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
