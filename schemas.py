from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional, List

class ResponsavelBase(BaseModel):
    nome_completo: str
    parentesco: Optional[str] = None
    telefone_1: Optional[str] = None
    telefone_2: Optional[str] = None
    email: Optional[str] = None

class ResponsavelResponse(ResponsavelBase):
    id_serial: int
    
    class Config:
        from_attributes = True

class ResidenteBase(BaseModel):
    nome_completo: str
    data_de_nascimento: date
    sexo: Optional[str] = None
    alergia: Optional[str] = "Nenhuma"
    quarto: Optional[str] = None

class ResidenteResumo(BaseModel):
    id_serial: int
    nome: str
    idade: int
    data_nascimento: date
    sexo: str
    alergia: str
    tarefas_pendentes: int
    proxima_tarefa: Optional[str] = None
    status: str
    
    class Config:
        from_attributes = True

class ResidenteDetalhado(BaseModel):
    id_serial: int
    nome_completo: str
    data_de_nascimento: date
    idade: int
    sexo: Optional[str]
    cpf: Optional[str]
    tipo_sanguineo: Optional[str]
    quarto: Optional[str]
    alergia: str
    convenio: Optional[str]
    observacoes_medicas: Optional[str]
    responsavel: Optional[ResponsavelResponse] = None
    
    class Config:
        from_attributes = True

    @field_validator('quarto', mode='before')
    @classmethod
    def formatar_quarto(cls, v):
        if v is not None and not isinstance(v, str):
            return getattr(v, 'numero', None)
        return v

class EstatisticasResponse(BaseModel):
    total: int
    com_tarefas: int
    concluidos: int

class PrescricaoBase(BaseModel):
    medicamentos_nome: str
    dosagem: str
    instrucoes: Optional[str] = None
    intervalo_horas: int

class PrescricaoResponse(PrescricaoBase):
    id_serial: int
    residente_id: int
    ativo: bool
    
    class Config:
        from_attributes = True

class MedicamentoPendente(BaseModel):
    id: int
    nome: str
    dosagem: str
    via: str
    horario: str
    status: str
    observacoes: Optional[str] = None
    
    class Config:
        from_attributes = True

class AdministrarMedicamentoRequest(BaseModel):
    status: str  # 'administrado' ou 'recusado'
    motivo_recusa: Optional[str] = None
    foto_evidencia: Optional[str] = None

class ConsultaBase(BaseModel):
    data_hora: datetime
    tipo_consulta: str
    local: str
    especialidade: str
    observacao: Optional[str] = None

class ConsultaResponse(BaseModel):
    id_serial: int
    residente_id: int
    medico_nome: Optional[str]
    data: str
    horario: str
    especialidade: str
    local: str
    status: str
    observacao: Optional[str]
    
    class Config:
        from_attributes = True

class ConcluirConsultaRequest(BaseModel):
    observacoes: Optional[str] = None
    diagnostico: Optional[str] = None
    prescricao: Optional[str] = None
    proximo_retorno: Optional[str] = None
    receita_foto: Optional[str] = None

class MedicamentoPendente(BaseModel):
    id: int
    nome: str
    dosagem: str
    via: str
    horario: str
    status: str
    observacoes: Optional[str] = None

class MedicamentoConcluido(BaseModel):
    id: int
    nome: str
    dosagem: str
    horario: str
    status: str
    responsavel: str

class AdministrarMedicamentoRequest(BaseModel):
    status: str  # 'administrado' ou 'recusado'
    motivo_recusa: Optional[str] = None
    foto_evidencia: Optional[str] = None

class ConsultaAgendada(BaseModel):
    id: str
    tipo: str
    especialidade: str
    medico: str
    data: str
    horario: str
    local: str
    status: str
    observacoes: Optional[str] = None

class PrepararConsultaRequest(BaseModel):
    documentos_preparados: bool

class ConcluirConsultaRequest(BaseModel):
    observacoes: Optional[str] = None
    novas_prescricoes: Optional[str] = None
    proximo_retorno: Optional[str] = None
    receita_uri: Optional[str] = None

class QuartoBase(BaseModel):
    numero: str
    andar: Optional[str] = None
    capacidade_maxima: int = 2
    tipo: Optional[str] = None

class QuartoResumo(BaseModel):
    quarto_id: int  
    numero: str
    andar: str
    ocupacao: int   
    capacidade: int 
    status_ocupacao: str
    
    class Config:
        from_attributes = True

class QuartoDetalhado(QuartoResumo):
    residentes_nomes: Optional[str] = None
    
    class Config:
        from_attributes = True

class ResidenteDoQuarto(BaseModel):
    residente_id: int
    nome: str
    idade: int
    sexo: str
    alergia: str
    tarefas_pendentes: int
    proxima_tarefa: Optional[str]
    status_tarefas: str
    
    class Config:
        from_attributes = True


class CadastrarCuidadorRequest(BaseModel):
    email: EmailStr
    senha: str

    nome_completo: str
    cpf: str                              
    telefone: Optional[str] = None
    especialidade: Optional[str] = None
    turno: Optional[str] = None           
    registro_profissional: Optional[str] = None
    quarto_ids: List[int] = []


class CuidadorListItem(BaseModel):
    id_serial: int
    nome_completo: str
    cpf: str
    telefone: Optional[str]
    especialidade: Optional[str]
    turno: Optional[str]
    status: str
    email: Optional[str]                  
    quartos: List[str] = []               

    class Config:
        from_attributes = True


class AtualizarQuartosRequest(BaseModel):
    quarto_ids: List[int]                 
