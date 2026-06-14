from sqlalchemy.orm import Session
from sqlalchemy import func, text, and_, or_
from models import Residente, ResidenteContato, Responsavel, Prescricao, HistoricoMedicacao
from datetime import datetime, date

def get_residentes_com_tarefas(db: Session):
    """
    Retorna todos os residentes ativos com contagem de tarefas pendentes
    """
    query = text("""
        SELECT 
            r.id_serial,
            r.nome_completo as nome,
            r.idade,
            r.data_de_nascimento as data_nascimento,
            r.sexo,
            r.alergia,
            COUNT(CASE WHEN h.status = 'pendente' THEN 1 END)::int as tarefas_pendentes,
            TO_CHAR(MIN(CASE 
                WHEN h.status = 'pendente' 
                THEN h.data_prevista 
            END), 'HH24:MI') as proxima_tarefa,
            CASE 
                WHEN COUNT(CASE WHEN h.status = 'pendente' AND h.data_prevista < NOW() THEN 1 END) > 0 
                    THEN 'atrasado'
                WHEN COUNT(CASE WHEN h.status = 'pendente' THEN 1 END) > 0 
                    THEN 'pendente'
                ELSE 'ok'
            END as status
        FROM residente r
        LEFT JOIN prescricao p ON r.id_serial = p.residente_id AND p.ativo = true
        LEFT JOIN historico_medicacao h ON p.id_serial = h.prescricao_id 
            AND DATE(h.data_prevista) = CURRENT_DATE
        WHERE r.status = 'ativo'
        GROUP BY r.id_serial, r.nome_completo, r.idade, r.data_de_nascimento, r.sexo, r.alergia
        ORDER BY r.nome_completo
    """)
    
    result = db.execute(query)
    return result.mappings().all()

def get_residente_detalhado(db: Session, residente_id: int):
    """
    Retorna informações detalhadas de um residente incluindo responsável
    """
    residente = db.query(Residente).filter(
        Residente.id_serial == residente_id,
        Residente.status == "ativo"
    ).first()
    
    if not residente:
        return None
    
    contato = db.query(ResidenteContato, Responsavel).join(
        Responsavel, ResidenteContato.responsavel_id == Responsavel.id_serial
    ).filter(
        ResidenteContato.residente_id == residente_id,
        ResidenteContato.ordem_chamada == 1
    ).first()
    
    residente_dict = {
        "id_serial": residente.id_serial,
        "nome_completo": residente.nome_completo,
        "data_de_nascimento": residente.data_de_nascimento,
        "idade": residente.idade,
        "sexo": residente.sexo,
        "cpf": residente.cpf,
        "tipo_sanguineo": residente.tipo_sanguineo,
        "quarto": residente.quarto,
        "alergia": residente.alergia,
        "convenio": residente.convenio,
        "observacoes_medicas": residente.observacoes_medicas,
        "responsavel": None
    }
    
    if contato:
        _, responsavel = contato
        residente_dict["responsavel"] = {
            "id_serial": responsavel.id_serial,
            "nome_completo": responsavel.nome_completo,
            "parentesco": responsavel.parentesco,
            "telefone_1": responsavel.telefone_1,
            "telefone_2": responsavel.telefone_2,
            "email": responsavel.email
        }
    
    return residente_dict

def get_estatisticas(db: Session):
    """
    Retorna estatísticas gerais dos residentes
    """
    residentes = get_residentes_com_tarefas(db)
    
    total = len(residentes)
    com_tarefas = sum(1 for r in residentes if r['tarefas_pendentes'] > 0)
    concluidos = total - com_tarefas
    
    return {
        "total": total,
        "com_tarefas": com_tarefas,
        "concluidos": concluidos
    }