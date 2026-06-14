from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud.quartos as crud_quartos
 
router = APIRouter(
    prefix="/api/quartos",
    tags=["Quartos"]
)
 
@router.get("/usuario/{usuario_id}")
def listar_quartos_usuario(
    usuario_id: int,
    nivel_acesso: str = "cuidador",
    db: Session = Depends(get_db)
):
    try:
        if nivel_acesso in ['admin', 'coordenador']:
            quartos = crud_quartos.get_todos_quartos(db)
        else:
            quartos = crud_quartos.get_quartos_cuidador(db, usuario_id)
        
        return [dict(q) for q in quartos]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar quartos: {str(e)}"
        )
 
@router.get("/{quarto_id}")
def obter_quarto(
    quarto_id: int,
    db: Session = Depends(get_db)
):
    """
    Retorna informações detalhadas de um quarto
    """
    try:
        quarto = crud_quartos.get_quarto_detalhes(db, quarto_id)
        
        if not quarto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quarto não encontrado"
            )
        
        return dict(quarto)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar quarto: {str(e)}"
        )
 
@router.get("/{quarto_id}/residentes")
def listar_residentes_quarto(
    quarto_id: int,
    db: Session = Depends(get_db)
):
    """
    Lista todos os residentes de um quarto
    """
    try:
        residentes = crud_quartos.get_residentes_quarto(db, quarto_id)
        return [dict(r) for r in residentes]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar residentes: {str(e)}"
        )
 
