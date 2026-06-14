from sqlalchemy.orm import Session
from sqlalchemy import text

def cadastrar_cuidador(db: Session, dados: dict):
    query = text("""
        SELECT * FROM fn_cadastrar_cuidador(
            :email, :senha, :nome_completo, :cpf,
            :telefone, :especialidade, :turno, :registro_prof,
            :quarto_ids
        )
    """)
    result = db.execute(query, {
        "email":          dados["email"].strip().lower(),
        "senha":          dados["senha"],
        "nome_completo":  dados["nome_completo"],
        "cpf":            dados["cpf"].replace(".", "").replace("-", ""),
        "telefone":       dados.get("telefone"),
        "especialidade":  dados.get("especialidade"),
        "turno":          dados.get("turno"),
        "registro_prof":  dados.get("registro_profissional"),
        "quarto_ids":     dados.get("quarto_ids", []),
    }).fetchone()
    db.commit()
    return result


def listar_cuidadores(db: Session):
    query = text("""
        SELECT
            c.id_serial,
            c.nome_completo,
            c.cpf,
            c.telefone,
            c.especialidade,
            c.turno,
            c.status,
            u.email,
            COALESCE(
                ARRAY_AGG(DISTINCT q.numero ORDER BY q.numero)
                FILTER (WHERE q.numero IS NOT NULL AND cq.ativo = TRUE),
                ARRAY[]::TEXT[]
            ) AS quartos
        FROM cuidador c
        LEFT JOIN usuarios u ON c.usuario_id = u.id_serial
        LEFT JOIN cuidador_quartos cq ON c.id_serial = cq.cuidador_id
        LEFT JOIN quartos q ON cq.quarto_id = q.id_serial AND q.ativo = TRUE
        GROUP BY c.id_serial, c.nome_completo, c.cpf, c.telefone,
                 c.especialidade, c.turno, c.status, u.email
        ORDER BY c.nome_completo
    """)
    result = db.execute(query)
    return result.mappings().all()


def atualizar_quartos_cuidador(db: Session, cuidador_id: int, quarto_ids: list):
    db.execute(
        text("UPDATE cuidador_quartos SET ativo = FALSE WHERE cuidador_id = :cid"),
        {"cid": cuidador_id}
    )
    for qid in quarto_ids:
        db.execute(text("""
            INSERT INTO cuidador_quartos (cuidador_id, quarto_id, ativo)
            VALUES (:cid, :qid, TRUE)
            ON CONFLICT (cuidador_id, quarto_id)
            DO UPDATE SET ativo = TRUE, updated_at = NOW()
        """), {"cid": cuidador_id, "qid": qid})
    db.commit()


def listar_quartos_disponiveis(db: Session):
    query = text("""
        SELECT id_serial, numero, andar, ocupacao_atual, capacidade_maxima,
               CASE
                   WHEN ocupacao_atual >= capacidade_maxima THEN 'cheio'
                   WHEN ocupacao_atual > 0 THEN 'parcial'
                   ELSE 'vazio'
               END AS status_ocupacao
        FROM quartos
        WHERE ativo = TRUE
        ORDER BY numero
    """)
    result = db.execute(query)
    return result.mappings().all()
