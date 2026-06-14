from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residentes, medicacao, consultas, quartos, auth, coordenador

app = FastAPI(
    title="API Sistema de Gestão de Asilo",
    description="API completa para gerenciamento de asilo",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(residentes.router)
app.include_router(medicacao.router)
app.include_router(consultas.router)
app.include_router(quartos.router)
app.include_router(auth.router)  
app.include_router(coordenador.router)

@app.get("/")
def root():
    return {
        "message": "API Sistema Asilo v2.0",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
