from sqlalchemy.orm import Session
from sqlalchemy import text
from models import Consulta
from datetime import datetime, date

def get_consultas_agendadas(db: Session, residente_id: int):
    """
    Retorna consultas agendadas de um residente (hoje e futuras)
    """
    query = text("""
        SELECT 
            CONCAT('c', c.id_serial) as id,
            'consulta' as tipo,
            c.especialidade,
            COALESCE(m.nome, 'Não informado') as medico,
            TO_CHAR(c.data_hora, 'DD/MM/YYYY') as data,
            TO_CHAR(c.data_hora, 'HH24:MI') as horario,
            c.local,
            c.status,
            c.observacao as observacoes
        FROM consultas c
        LEFT JOIN medico m ON c.medico_id = m.id_serial
        WHERE c.residente_id = :residente_id
            AND c.data_hora >= CURRENT_DATE
            AND c.status = 'agendada'
        ORDER BY c.data_hora
    """)
    
    result = db.execute(query, {"residente_id": residente_id})
    return result.mappings().all()

def preparar_residente_consulta(db: Session, consulta_id: int):
    """
    Marca que residente está preparado para consulta
    """
    # Remove o prefixo 'c' do ID se houver
    if isinstance(consulta_id, str) and consulta_id.startswith('c'):
        consulta_id = int(consulta_id[1:])
    
    consulta = db.query(Consulta).filter(
        Consulta.id_serial == consulta_id
    ).first()
    
    if not consulta:
        return None
    
    return consulta

def concluir_consulta(
    db: Session,
    consulta_id: int,
    observacoes: str = None,
    novas_prescricoes: str = None,
    proximo_retorno: str = None,
    receita_uri: str = None
):
    """
    Marca consulta como realizada e salva informações
    """
    if isinstance(consulta_id, str) and consulta_id.startswith('c'):
        consulta_id = int(consulta_id[1:])
    
    consulta = db.query(Consulta).filter(
        Consulta.id_serial == consulta_id
    ).first()
    
    if not consulta:
        return None
    
    consulta.status = 'realizada'
    consulta.observacao = observacoes
    consulta.prescricao = novas_prescricoes
    consulta.proximo_retorno = proximo_retorno
    
    if receita_uri:
        consulta.laudo = receita_uri
    
    db.commit()
    db.refresh(consulta)
    
    return consulta

def get_relatorio_residente(db: Session, residente_id: int):
    query_consultas = text("""
        SELECT c.data_hora, c.especialidade, c.local, c.observacao, c.prescricao
        FROM consultas c
        WHERE c.residente_id = :residente_id AND c.status = 'realizada'
        ORDER BY c.data_hora DESC
    """)
    consultas = db.execute(query_consultas, {"residente_id": residente_id}).mappings().all()

    query_medicamentos = text("""
        SELECT h.data_execucao, p.medicamentos_nome, p.dosagem, h.status, h.observacao
        FROM historico_medicacao h
        JOIN prescricao p ON h.prescricao_id = p.id_serial
        WHERE p.residente_id = :residente_id AND h.status IN ('administrado', 'recusado')
        ORDER BY h.data_execucao DESC
    """)
    medicamentos = db.execute(query_medicamentos, {"residente_id": residente_id}).mappings().all()

    return {
        "consultas": consultas,
        "medicamentos": medicamentos
    }
