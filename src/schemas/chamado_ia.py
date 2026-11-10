"""
DTOs e Schemas Pydantic para a Triagem Inteligente ZelaFix
Alinhados ao contrato do ZelaFix Mobile e Backend Java Spring Boot
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class LocalizacaoDTO(BaseModel):
    logradouro: Optional[str] = Field(None, example="Avenida Paulista")
    numero: Optional[str] = Field(None, example="1578")
    bairro: Optional[str] = Field(None, example="Bela Vista")
    cidade: Optional[str] = Field("São Paulo", example="São Paulo")
    cep: Optional[str] = Field(None, example="01310-200")
    latitude: Optional[float] = Field(-23.5629, example=-23.5629)
    longitude: Optional[float] = Field(-46.6544, example=-46.6544)

class TriagemRequestDTO(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=200, example="Buraco profundo na faixa de rolamento")
    categoria: str = Field(..., example="Buraco na Rua")
    descricao: str = Field("", max_length=2000, example="Cratera aberta com mais de 8cm após chuva forte, risco de acidentes.")
    fotoUrl: Optional[str] = Field(None, example="https://images.unsplash.com/photo-1515162816999-a0c47dc192f7")
    imageBase64: Optional[str] = Field(None, description="Imagem em base64 para análise direta de visão computacional")
    localizacao: Optional[LocalizacaoDTO] = None
    apoiosCount: Optional[int] = Field(0, ge=0, example=28, description="Número de apoios (+1) recebidos da comunidade")
    autorId: Optional[str] = Field(None, example="usr_12345")
    telemetriaIot: Optional[Dict[str, Any]] = Field(None, description="Leituras opcionais de sensores urbanos IoT")

class AnaliseVisualResumo(BaseModel):
    categoriaDetectada: str
    confiancaScore: float
    severidadeVisual: str
    caracteristicasExtraidas: Dict[str, Any]

class RagEvidenciaResumo(BaseModel):
    documentoFonte: str
    trechoRelevante: str
    artigoOuNorma: str
    similaridadeScore: float

class IotResumo(BaseModel):
    sensorPresente: bool
    tipoSensor: Optional[str] = None
    anomaliaDetectada: bool
    detalhesLeitura: Optional[Dict[str, Any]] = None

class IobResumo(BaseModel):
    socialUrgencyScore: float
    nivelEngajamento: str
    reputacaoCidadao: float
    ajustePrioridadeComunitario: bool

class TriagemResponseDTO(BaseModel):
    # Campos de primeiro nível esperados diretamente pelo aplicativo Mobile
    prioridade: str = Field(..., example="Crítica", description="Baixa | Média | Alta | Crítica")
    orgaoResponsavel: str = Field(..., example="Subprefeitura — Equipe de Pavimentação e Tapa-Buraco")
    parecerIa: str = Field(..., example="Laudo Técnico Oficial gerado por IA...")
    
    # Metadados e evidências do aprofundamento técnico (Visão Computacional, RAG, IoT e IoB)
    slaSugeridoHoras: int = Field(24, example=24)
    enquadramentoLegal: str = Field(..., example="Decreto Municipal nº 59.150/2019, Art. 4º")
    riscoPotencial: str = Field(..., example="Alto risco de queda para motociclistas e danos estruturais")
    checklistVistoria: List[str] = Field(default_factory=list)
    analiseVisual: Optional[AnaliseVisualResumo] = None
    evidenciasRag: Optional[List[RagEvidenciaResumo]] = None
    telemetriaIot: Optional[IotResumo] = None
    analiseIob: Optional[IobResumo] = None
    provedorGenAi: str = Field("Google Gemini 2.5 Flash (ou Heurístico de Alta Fidelidade)")
    statusExecucao: str = Field("SUCESSO")

class ChatMessageDTO(BaseModel):
    role: str = Field("user", example="user", description="user | assistant | system")
    content: str = Field(..., example="Qual o prazo para a prefeitura tampar um buraco?")

class ChatCidadaoRequestDTO(BaseModel):
    mensagem: str = Field(..., min_length=1, max_length=1000, example="Como faço para pedir a poda de uma árvore que está caindo?")
    historico: Optional[List[ChatMessageDTO]] = Field(default_factory=list)
    bairro: Optional[str] = Field(None, example="Bela Vista")

class ChatCidadaoResponseDTO(BaseModel):
    resposta: str
    baseLegalUtilizada: Optional[str] = None
    orgaoCompetenteSugerido: Optional[str] = None
    telefonesUteis: List[str] = Field(default_factory=lambda: ["Prefeitura: 156", "Defesa Civil: 199", "Bombeiros: 193"])
    sugestaoAberturaChamado: bool = False
    categoriaSugerida: Optional[str] = None

