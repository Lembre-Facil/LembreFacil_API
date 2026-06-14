from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import CadastrarCuidadorRequest, AtualizarQuartosRequest
import crud.coordenador as crud

router = APIRouter(
    prefix="/api/coordenador",
    tags=["Coordenador"]
)


@router.get("/cuidadores")
def listar_cuidadores(db: Session = Depends(get_db)):
    try:
        cuidadores = crud.listar_cuidadores(db)
        return [dict(c) for c in cuidadores]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cuidadores", status_code=201)
def cadastrar_cuidador(
    dados: CadastrarCuidadorRequest,
    db: Session = Depends(get_db)
):
    result = crud.cadastrar_cuidador(db, dados.model_dump())

    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)

    return {
        "success": True,
        "message": result.message,
        "cuidador_id": result.cuidador_id,
        "usuario_id": result.usuario_id,
    }


@router.put("/cuidadores/{cuidador_id}/quartos")
def atualizar_quartos(
    cuidador_id: int,
    body: AtualizarQuartosRequest,
    db: Session = Depends(get_db)
):
    try:
        crud.atualizar_quartos_cuidador(db, cuidador_id, body.quarto_ids)
        return {"success": True, "message": "Quartos atualizados"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quartos")
def listar_quartos(db: Session = Depends(get_db)):
    try:
        quartos = crud.listar_quartos_disponiveis(db)
        return [dict(q) for q in quartos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
