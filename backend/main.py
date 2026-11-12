from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import filmes, clientes, locacoes

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

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
