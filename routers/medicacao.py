from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from database import get_db
import schemas
import crud.medicacao as crud_med

router = APIRouter(
    prefix="/api/tarefas/medicacao",
    tags=["Medicação - Tarefas"]
)

@router.get("/residente/{residente_id}/pendentes", response_model=List[schemas.MedicamentoPendente])
def listar_pendentes(
    residente_id: int,
    data: date = None,
    db: Session = Depends(get_db)
):
    """
    Lista medicamentos pendentes de um residente
    """
    try:
        medicamentos = crud_med.get_medicamentos_pendentes(db, residente_id, data)
        return medicamentos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar medicamentos: {str(e)}"
        )

@router.get("/residente/{residente_id}/concluidos", response_model=List[schemas.MedicamentoConcluido])
def listar_concluidos(
    residente_id: int,
    data: date = None,
    db: Session = Depends(get_db)
):
    """
    Lista medicamentos concluídos hoje
    """
    try:
        medicamentos = crud_med.get_medicamentos_concluidos(db, residente_id, data)
        return medicamentos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )

@router.post("/{historico_id}/administrar")
def administrar(
    historico_id: int,
    request: schemas.AdministrarMedicamentoRequest,
    cuidador_id: int = 1,  # TODO: Pegar do JWT token
    db: Session = Depends(get_db)
):
    """
    Administra ou recusa medicamento
    """
    try:
        historico = crud_med.administrar_medicamento(
            db=db,
            historico_id=historico_id,
            cuidador_id=cuidador_id,
            status=request.status,
            motivo_recusa=request.motivo_recusa,
            foto_evidencia=request.foto_evidencia
        )
        
        if not historico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medicamento não encontrado"
            )
        
        return {
            "message": f"Medicamento {request.status} com sucesso",
            "id": historico.id_serial
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao administrar medicamento: {str(e)}"
        )