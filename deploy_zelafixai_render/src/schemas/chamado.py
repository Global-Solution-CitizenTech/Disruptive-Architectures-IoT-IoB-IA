"""
Schemas Pydantic: Contexto do Chamado Municipal de Zeladoria Urbana — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TelemetriaIotPayload(BaseModel):
    device_id: Optional[str] = Field(default=None, description="Identificador do sensor urbano (ex: IOT-VIB-01)")
    tipo_sensor: Optional[str] = Field(default=None, description="Tipo de sensor: acelerometro, ultrassom_bueiro, fotocelula")
    valor_medido: Optional[float] = Field(default=None, description="Valor numérico aferido pelo sensor físico")
    unidade: Optional[str] = Field(default=None, description="Unidade de medida (G, %, lux, cm)")
    anomalia_detectada: Optional[bool] = Field(default=False, description="Flag de limiar de anomalia física na borda")

class ChamadoContextPayload(BaseModel):
    id: Optional[int] = Field(default=None, description="Identificador único do chamado na base relacional")
    protocolo: Optional[str] = Field(default=None, description="Código de protocolo público (ex: ZF-2026-0042)")
    categoria: str = Field(..., description="Categoria urbana: 'Buraco na Rua', 'Iluminação Pública', 'Drenagem/Bueiro', 'Lixo/Entulho', 'Manejo Arbóreo', 'Sinalização', 'Vazamento Água/Esgoto', 'Calçadas'")
    titulo: str = Field(..., description="Título resumido da ocorrência urbana")
    descricao: Optional[str] = Field(default="", description="Detalhamento fático fornecido pelo munícipe")
    bairro: Optional[str] = Field(default=None, description="Bairro ou distrito da ocorrência")
    logradouro: Optional[str] = Field(default=None, description="Nome da rua ou avenida")
    numero: Optional[str] = Field(default=None, description="Número aproximado")
    cep: Optional[str] = Field(default=None, description="Código de Endereçamento Postal")
    latitude: Optional[float] = Field(default=None, description="Coordenada geográfica de latitude")
    longitude: Optional[float] = Field(default=None, description="Coordenada geográfica de longitude")
    apoios_comunitarios: Optional[int] = Field(default=0, description="Quantidade de confirmações +1 da vizinhança (IoB)")
    foto_url: Optional[str] = Field(default=None, description="URL pública ou caminho da evidência fotográfica")
    foto_base64: Optional[str] = Field(default=None, description="Foto da ocorrência codificada em Base64 para visão computacional")
    telemetria_iot: Optional[TelemetriaIotPayload] = Field(default=None, description="Telemetria de sensores urbanos de IoT")
