from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import schemas
import crud.residentes as crud

router = APIRouter(
    prefix="/api/residentes",
    tags=["Residentes"]
)

@router.get("/", response_model=List[schemas.ResidenteResumo])
def listar_residentes(db: Session = Depends(get_db)):
    """
    Lista todos os residentes ativos com resumo de tarefas do dia
    """
    try:
        residentes = crud.get_residentes_com_tarefas(db)
        return residentes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar residentes: {str(e)}"
        )

@router.get("/estatisticas", response_model=schemas.EstatisticasResponse)
def obter_estatisticas(db: Session = Depends(get_db)):
    """
    Retorna estatísticas gerais (total, com tarefas, concluídos)
    """
    try:
        return crud.get_estatisticas(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )

@router.get("/{residente_id}", response_model=schemas.ResidenteDetalhado)
def obter_residente(residente_id: int, db: Session = Depends(get_db)):
    """
    Retorna informações detalhadas de um residente
    """
    residente = crud.get_residente_detalhado(db, residente_id)
    
    if not residente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Residente não encontrado"
        )
    
    return residente