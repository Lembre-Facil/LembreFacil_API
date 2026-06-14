from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from crud.consultas import concluir_consulta, get_consultas_agendadas, get_relatorio_residente
import schemas
import crud.consultas as crud_cons

router = APIRouter(
    prefix="/api/tarefas/consultas",
    tags=["Consultas - Tarefas"]
)

@router.get("/residente/{residente_id}", response_model=List[schemas.ConsultaAgendada])
def listar_consultas(
    residente_id: int,
    db: Session = Depends(get_db)
):
    """
    Lista consultas agendadas de um residente
    """
    try:
        consultas = crud_cons.get_consultas_agendadas(db, residente_id)
        return consultas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar consultas: {str(e)}"
        )

@router.get("/residentes/{residente_id}/relatorio")
def gerar_dados_relatorio(residente_id: int, db: Session = Depends(get_db)):
    try:
        dados = get_relatorio_residente(db, residente_id)
        return {"success": True, "data": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{consulta_id}/preparar")
def preparar_residente(
    consulta_id: str,
    request: schemas.PrepararConsultaRequest,
    db: Session = Depends(get_db)
):
    """
    Marca que residente foi preparado para consulta
    """
    try:
        consulta = crud_cons.preparar_residente_consulta(db, consulta_id)
        
        if not consulta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta não encontrada"
            )
        
        return {
            "message": "Residente preparado com sucesso",
            "consulta_id": consulta.id_serial
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao preparar residente: {str(e)}"
        )

@router.post("/{consulta_id}/concluir")
def concluir(
    consulta_id: str,
    request: schemas.ConcluirConsultaRequest,
    db: Session = Depends(get_db)
):
    """
    Conclui consulta e salva informações
    """
    try:
        consulta = crud_cons.concluir_consulta(
            db=db,
            consulta_id=consulta_id,
            observacoes=request.observacoes,
            novas_prescricoes=request.novas_prescricoes,
            proximo_retorno=request.proximo_retorno,
            receita_uri=request.receita_uri
        )
        
        if not consulta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta não encontrada"
            )
        
        return {
            "message": "Consulta concluída com sucesso",
            "consulta_id": consulta.id_serial
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao concluir consulta: {str(e)}"
        )
