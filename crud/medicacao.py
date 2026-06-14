from sqlalchemy.orm import Session
from sqlalchemy import text
from models import HistoricoMedicacao, Prescricao
from datetime import datetime, date, timedelta

def get_medicamentos_pendentes(db: Session, residente_id: int, data: date = None):
    """Retorna medicamentos pendentes de um residente"""
    if data is None:
        data = date.today()
    
    query = text("""
        SELECT 
            h.id_serial as id,
            p.medicamentos_nome as nome,
            p.dosagem,
            'Oral' as via,
            TO_CHAR(h.data_prevista, 'HH24:MI') as horario,
            h.status,
            p.instrucoes as observacoes
        FROM historico_medicacao h
        INNER JOIN prescricao p ON h.prescricao_id = p.id_serial
        WHERE p.residente_id = :residente_id
            AND DATE(h.data_prevista) = :data
            AND h.status = 'pendente'
        ORDER BY h.data_prevista
    """)
    
    result = db.execute(query, {"residente_id": residente_id, "data": data})
    return result.mappings().all()

def get_medicamentos_concluidos(db: Session, residente_id: int, data: date = None):
    """Retorna medicamentos concluídos hoje"""
    if data is None:
        data = date.today()
    
    query = text("""
        SELECT 
            h.id_serial as id,
            p.medicamentos_nome as nome,
            p.dosagem,
            TO_CHAR(h.data_execucao, 'HH24:MI') as horario,
            h.status,
            COALESCE(c.nome_completo, 'Sistema') as responsavel
        FROM historico_medicacao h
        INNER JOIN prescricao p ON h.prescricao_id = p.id_serial
        LEFT JOIN cuidador c ON h.cuidador_id = c.id_serial
        WHERE p.residente_id = :residente_id
            AND DATE(h.data_prevista) = :data
            AND h.status IN ('administrado', 'recusado')
        ORDER BY h.data_execucao DESC
    """)
    
    result = db.execute(query, {"residente_id": residente_id, "data": data})
    return result.mappings().all()

def criar_proximo_agendamento(db: Session, prescricao_id: int, data_base: datetime):
    """
    Cria o próximo agendamento baseado no intervalo
    """
    prescricao = db.query(Prescricao).filter(
        Prescricao.id_serial == prescricao_id,
        Prescricao.ativo == True
    ).first()
    
    if not prescricao or not prescricao.intervalo_horas:
        return None
    
    proxima_data = data_base + timedelta(hours=prescricao.intervalo_horas)
    
    if prescricao.data_fim and proxima_data.date() > prescricao.data_fim:
        return None

    existe = db.query(HistoricoMedicacao).filter(
        HistoricoMedicacao.prescricao_id == prescricao_id,
        HistoricoMedicacao.data_prevista == proxima_data
    ).first()
    
    if existe:
        return existe  
    
    novo = HistoricoMedicacao(
        prescricao_id=prescricao_id,
        data_prevista=proxima_data,
        status='pendente',
        observacao='Agendamento automático'
    )
    
    db.add(novo)
    db.commit()
    db.refresh(novo)
    
    print(f"Próximo agendamento criado: {proxima_data}")
    
    return novo

def administrar_medicamento(
    db: Session,
    historico_id: int,
    cuidador_id: int,
    status: str,
    motivo_recusa: str = None,
    foto_evidencia: str = None
):
    """
    Registra administração/recusa
    """
    historico = db.query(HistoricoMedicacao).filter(
        HistoricoMedicacao.id_serial == historico_id
    ).first()
    
    if not historico:
        return None
    
    historico.cuidador_id = cuidador_id
    historico.data_execucao = datetime.now()
    historico.status = status
    
    if status == 'recusado':
        historico.motivo_recusa = motivo_recusa
        historico.foto_evidencia = foto_evidencia
    
    db.commit()
    db.refresh(historico)
    
    if status == 'administrado':
        criar_proximo_agendamento(
            db=db,
            prescricao_id=historico.prescricao_id,
            data_base=historico.data_execucao
        )
    
    return historico

def gerar_agendamentos_inicial(db: Session, prescricao_id: int, dias: int = 7):
    """
    Gera agendamentos iniciais quando cria prescrição
    """
    prescricao = db.query(Prescricao).filter(
        Prescricao.id_serial == prescricao_id,
        Prescricao.ativo == True
    ).first()
    
    if not prescricao or not prescricao.intervalo_horas:
        return []
    
    criados = []
    proxima = datetime.now()
    limite = datetime.now() + timedelta(days=dias)
    
    while proxima <= limite:
        if prescricao.data_fim and proxima.date() > prescricao.data_fim:
            break
        
        existe = db.query(HistoricoMedicacao).filter(
            HistoricoMedicacao.prescricao_id == prescricao_id,
            HistoricoMedicacao.data_prevista == proxima
        ).first()
        
        if not existe:
            novo = HistoricoMedicacao(
                prescricao_id=prescricao_id,
                data_prevista=proxima,
                status='pendente'
            )
            db.add(novo)
            criados.append(novo)
        
        proxima += timedelta(hours=prescricao.intervalo_horas)
    
    db.commit()
    return criados