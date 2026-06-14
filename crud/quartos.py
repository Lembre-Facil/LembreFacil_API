from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date

def get_quartos_cuidador(db: Session, cuidador_id: int):
    """
    Retorna quartos atribuídos a um cuidador com resumo de tarefas
    """
    query = text("""
        SELECT 
            q.id_serial as quarto_id,
            q.numero,
            q.andar,
            q.ocupacao_atual as ocupacao,
            q.capacidade_maxima as capacidade,
            COUNT(DISTINCT CASE 
                WHEN h.status = 'pendente' AND DATE(h.data_prevista) = CURRENT_DATE 
                THEN r.id_serial 
            END)::int as residentes_com_tarefas,
            COUNT(DISTINCT r.id_serial)::int as total_residentes,
            CASE 
                WHEN q.ocupacao_atual >= q.capacidade_maxima THEN 'cheio'
                WHEN q.ocupacao_atual > 0 THEN 'parcial'
                ELSE 'vazio'
            END as status_ocupacao
        FROM quartos q
        INNER JOIN cuidador_quartos cq ON q.id_serial = cq.quarto_id
        LEFT JOIN residente r ON q.id_serial = r.quarto_id AND r.status = 'ativo'
        LEFT JOIN prescricao p ON r.id_serial = p.residente_id AND p.ativo = TRUE
        LEFT JOIN historico_medicacao h ON p.id_serial = h.prescricao_id 
            AND DATE(h.data_prevista) = CURRENT_DATE
        WHERE cq.cuidador_id = :cuidador_id
            AND cq.ativo = TRUE
            AND q.ativo = TRUE
        GROUP BY q.id_serial, q.numero, q.andar, q.ocupacao_atual, q.capacidade_maxima
        ORDER BY q.numero
    """)
    
    result = db.execute(query, {"cuidador_id": cuidador_id})
    quartos = result.mappings().all()
    
    # Debug: Ver o que está retornando
    print(f"Quartos encontrados para cuidador {cuidador_id}: {len(quartos)}")
    for q in quartos:
        print(f"   Quarto {q['numero']}: {q['total_residentes']} residentes, {q['residentes_com_tarefas']} com tarefas")
    
    return quartos

def get_residentes_quarto(db: Session, quarto_id: int):
    """
    Retorna residentes de um quarto com suas tarefas
    """
    query = text("""
        SELECT 
            r.id_serial as residente_id,
            r.nome_completo as nome,
            r.idade,
            r.sexo,
            r.alergia,
            COUNT(DISTINCT CASE 
                WHEN h.status = 'pendente' AND DATE(h.data_prevista) = CURRENT_DATE 
                THEN h.id_serial 
            END)::int as tarefas_pendentes,
            TO_CHAR(MIN(CASE 
                WHEN h.status = 'pendente' 
                THEN h.data_prevista 
            END), 'HH24:MI') as proxima_tarefa,
            CASE 
                WHEN COUNT(CASE 
                    WHEN h.status = 'pendente' AND h.data_prevista < NOW() 
                    THEN 1 
                END) > 0 THEN 'atrasado'
                WHEN COUNT(CASE 
                    WHEN h.status = 'pendente' 
                    THEN 1 
                END) > 0 THEN 'pendente'
                ELSE 'ok'
            END as status_tarefas
        FROM residente r
        LEFT JOIN prescricao p ON r.id_serial = p.residente_id AND p.ativo = TRUE
        LEFT JOIN historico_medicacao h ON p.id_serial = h.prescricao_id 
            AND DATE(h.data_prevista) = CURRENT_DATE
        WHERE r.quarto_id = :quarto_id
            AND r.status = 'ativo'
        GROUP BY r.id_serial, r.nome_completo, r.idade, r.sexo, r.alergia
        ORDER BY r.nome_completo
    """)
    
    result = db.execute(query, {"quarto_id": quarto_id})
    residentes = result.mappings().all()
    
    print(f"Residentes encontrados no quarto {quarto_id}: {len(residentes)}")
    
    return residentes

def get_quarto_detalhes(db: Session, quarto_id: int):
    """
    Retorna detalhes completos de um quarto
    """
    query = text("""
        SELECT 
            q.id_serial,
            q.numero,
            q.andar,
            q.ocupacao_atual,
            q.capacidade_maxima,
            q.tipo,
            COUNT(DISTINCT CASE 
                WHEN h.status = 'pendente' AND DATE(h.data_prevista) = CURRENT_DATE 
                THEN r.id_serial 
            END)::int as residentes_com_tarefas,
            COUNT(DISTINCT r.id_serial)::int as total_residentes,
            STRING_AGG(DISTINCT r.nome_completo, ', ' ORDER BY r.nome_completo) as residentes_nomes,
            CASE 
                WHEN q.ocupacao_atual >= q.capacidade_maxima THEN 'cheio'
                WHEN q.ocupacao_atual > 0 THEN 'parcial'
                ELSE 'vazio'
            END as status_ocupacao
        FROM quartos q
        LEFT JOIN residente r ON q.id_serial = r.quarto_id AND r.status = 'ativo'
        LEFT JOIN prescricao p ON r.id_serial = p.residente_id AND p.ativo = TRUE
        LEFT JOIN historico_medicacao h ON p.id_serial = h.prescricao_id 
            AND DATE(h.data_prevista) = CURRENT_DATE
        WHERE q.id_serial = :quarto_id
            AND q.ativo = TRUE
        GROUP BY q.id_serial, q.numero, q.andar, q.ocupacao_atual, q.capacidade_maxima, q.tipo
    """)
    
    result = db.execute(query, {"quarto_id": quarto_id})
    return result.mappings().first()

def get_todos_quartos(db: Session):
    """
    Retorna TODOS os quartos para administradores e coordenadores
    """
    query = text("""
        SELECT 
            q.id_serial as quarto_id,
            q.numero,
            q.andar,
            q.ocupacao_atual as ocupacao,
            q.capacidade_maxima as capacidade,
            COUNT(DISTINCT CASE 
                WHEN h.status = 'pendente' AND DATE(h.data_prevista) = CURRENT_DATE 
                THEN r.id_serial 
            END)::int as residentes_com_tarefas,
            COUNT(DISTINCT r.id_serial)::int as total_residentes,
            CASE 
                WHEN q.ocupacao_atual >= q.capacidade_maxima THEN 'cheio'
                WHEN q.ocupacao_atual > 0 THEN 'parcial'
                ELSE 'vazio'
            END as status_ocupacao
        FROM quartos q
        LEFT JOIN residente r ON q.id_serial = r.quarto_id AND r.status = 'ativo'
        LEFT JOIN prescricao p ON r.id_serial = p.residente_id AND p.ativo = TRUE
        LEFT JOIN historico_medicacao h ON p.id_serial = h.prescricao_id 
            AND DATE(h.data_prevista) = CURRENT_DATE
        WHERE q.ativo = TRUE
        GROUP BY q.id_serial, q.numero, q.andar, q.ocupacao_atual, q.capacidade_maxima
        ORDER BY q.numero
    """)
    result = db.execute(query)
    return result.mappings().all()
