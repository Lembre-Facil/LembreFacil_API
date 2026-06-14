from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from sqlalchemy import text
 
router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticação"]
)
 
class LoginRequest(BaseModel):
    email: str
    senha: str
 
@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    try:
        query = text("SELECT * FROM fn_autenticar_usuario(CAST(:email AS TEXT), CAST(:senha AS TEXT))")
        result = db.execute(query, {
            "email": credentials.email.strip().lower(),
            "senha": credentials.senha
        }).fetchone()
 
        if not result:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
 
        if not result.success:
            raise HTTPException(status_code=401, detail=result.message)
 
        print(f"✅ Login: {result.pessoa_nome} ({result.nivel_acesso})")
        print(f"   Quartos permitidos: {result.quartos_permitidos}")
 
        return {
            "success":            result.success,
            "message":            result.message,
            "usuario_id":         result.usuario_id,
            "email":              result.email,
            "nivel_acesso":       result.nivel_acesso,
            "pessoa_id":          result.pessoa_id,
            "pessoa_nome":        result.pessoa_nome,
            "quartos_permitidos": result.quartos_permitidos,
        }
 
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no servidor: {str(e)}"
        )
 
