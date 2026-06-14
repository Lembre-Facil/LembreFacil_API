from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, ForeignKey, Enum, CHAR
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

# ============================================
# ENUMS
# ============================================

class NivelAcessoEnum(str, enum.Enum):
    cuidador = "cuidador"
    coordenador = "coordenador"
    admin = "admin"

class TurnoEnum(str, enum.Enum):
    manha = "manha"
    tarde = "tarde"
    noite = "noite"
    integral = "integral"

class StatusCuidadorEnum(str, enum.Enum):
    ativo = "ativo"
    inativo = "inativo"
    ferias = "ferias"

class SexoEnum(str, enum.Enum):
    masculino = "Masculino"
    feminino = "Feminino"
    outro = "Outro"

class StatusResidenteEnum(str, enum.Enum):
    ativo = "ativo"
    inativo = "inativo"
    transferido = "transferido"
    falecido = "falecido"

class StatusConsultaEnum(str, enum.Enum):
    agendada = "agendada"
    realizada = "realizada"
    cancelada = "cancelada"
    remarcada = "remarcada"

class StatusMedicacaoEnum(str, enum.Enum):
    pendente = "pendente"
    administrado = "administrado"
    recusado = "recusado"
    cancelado = "cancelado"

# ============================================
# MODELS
# ============================================

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    nivel_acesso = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cuidador = relationship("Cuidador", back_populates="usuario", uselist=False)

class Cuidador(Base):
    __tablename__ = "cuidador"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(100), nullable=False)
    cpf = Column(CHAR(11), unique=True, nullable=False)
    registro_profissional = Column(String(20))
    telefone = Column(String(15))
    especialidade = Column(String(50))
    turno = Column(String(20))
    status = Column(String(20), default="ativo")
    usuario_id = Column(Integer, ForeignKey("usuarios.id_serial"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    usuario = relationship("Usuario", back_populates="cuidador")
    historico_medicacao = relationship("HistoricoMedicacao", back_populates="cuidador")
    quartos = relationship("CuidadorQuarto", back_populates="cuidador")

class Responsavel(Base):
    __tablename__ = "responsavel"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(100), nullable=False)
    cpf = Column(CHAR(11), unique=True)
    parentesco = Column(String(20))
    telefone_1 = Column(String(15))
    telefone_2 = Column(String(15))
    email = Column(String(100))
    endereco_completo = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contatos = relationship("ResidenteContato", back_populates="responsavel")

class Residente(Base):
    __tablename__ = "residente"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(100), nullable=False, index=True)
    data_de_nascimento = Column(Date, nullable=False)
    cpf = Column(CHAR(11), unique=True)
    sexo = Column(String(15))
    tipo_sanguineo = Column(String(3))
    data_admissao = Column(Date, default=datetime.utcnow)
    status = Column(String(20), default="ativo", index=True)
    quarto_id = Column(Integer, ForeignKey("quartos.id_serial"))
    observacoes_medicas = Column(Text)
    alergia = Column(String(200), default="Nenhuma")
    idade = Column(Integer)
    convenio = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quarto = relationship("Quarto", back_populates="residentes")
    contatos = relationship("ResidenteContato", back_populates="residente")
    prescricoes = relationship("Prescricao", back_populates="residente")
    consultas = relationship("Consulta", back_populates="residente")

class ResidenteContato(Base):
    __tablename__ = "residente_contatos"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    residente_id = Column(Integer, ForeignKey("residente.id_serial"), nullable=False)
    responsavel_id = Column(Integer, ForeignKey("responsavel.id_serial"), nullable=False)
    ordem_chamada = Column(Integer, default=1)
    observacao = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    residente = relationship("Residente", back_populates="contatos")
    responsavel = relationship("Responsavel", back_populates="contatos")

class Medico(Base):
    __tablename__ = "medico"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    especialidade = Column(String(50))
    clinica_hospital = Column(String(100))
    observacao = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    consultas = relationship("Consulta", back_populates="medico")

class Consulta(Base):
    __tablename__ = "consultas"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    residente_id = Column(Integer, ForeignKey("residente.id_serial"), nullable=False)
    medico_id = Column(Integer, ForeignKey("medico.id_serial"))
    data_hora = Column(DateTime, nullable=False, index=True)
    tipo_consulta = Column(String(50))
    local = Column(String(100))
    especialidade = Column(String(50))
    observacao = Column(Text)
    diagnostico = Column(Text)
    prescricao = Column(Text)
    status = Column(String(20), default="agendada", index=True)
    proximo_retorno = Column(Text)
    laudo = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    residente = relationship("Residente", back_populates="consultas")
    medico = relationship("Medico", back_populates="consultas")

class Prescricao(Base):
    __tablename__ = "prescricao"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    residente_id = Column(Integer, ForeignKey("residente.id_serial"), nullable=False)
    medicamentos_nome = Column(String(100), nullable=False)
    dosagem = Column(String(50))
    instrucoes = Column(Text)
    intervalo_horas = Column(Integer)
    data_inicio = Column(Date, default=datetime.utcnow)
    data_fim = Column(Date)
    ativo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    residente = relationship("Residente", back_populates="prescricoes")
    historico = relationship("HistoricoMedicacao", back_populates="prescricao")

class HistoricoMedicacao(Base):
    __tablename__ = "historico_medicacao"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    prescricao_id = Column(Integer, ForeignKey("prescricao.id_serial"), nullable=False)
    cuidador_id = Column(Integer, ForeignKey("cuidador.id_serial"))
    data_prevista = Column(DateTime, nullable=False, index=True)
    data_execucao = Column(DateTime)
    status = Column(String(20), default="pendente", index=True)
    motivo_recusa = Column(Text)
    foto_evidencia = Column(Text)
    observacao = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prescricao = relationship("Prescricao", back_populates="historico")
    cuidador = relationship("Cuidador", back_populates="historico_medicacao")

class Quarto(Base):
    __tablename__ = "quartos"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), unique=True, nullable=False, index=True)
    andar = Column(String(10))
    capacidade_maxima = Column(Integer, default=2)
    ocupacao_atual = Column(Integer, default=0)
    tipo = Column(String(20))
    observacoes = Column(Text)
    ativo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    residentes = relationship("Residente", back_populates="quarto")
    cuidadores = relationship("CuidadorQuarto", back_populates="quarto")

class CuidadorQuarto(Base):
    __tablename__ = "cuidador_quartos"
    
    id_serial = Column(Integer, primary_key=True, index=True)
    cuidador_id = Column(Integer, ForeignKey("cuidador.id_serial"), nullable=False)
    quarto_id = Column(Integer, ForeignKey("quartos.id_serial"), nullable=False)
    data_atribuicao = Column(Date, default=datetime.utcnow)
    ativo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cuidador = relationship("Cuidador", back_populates="quartos")
    quarto = relationship("Quarto", back_populates="cuidadores")
    