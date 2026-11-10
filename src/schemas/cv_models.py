"""
DTOs para o módulo de Visão Computacional
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ImageAnalysisRequest(BaseModel):
    image_url: Optional[str] = Field(None, example="https://images.unsplash.com/photo-1515162816999-a0c47dc192f7")
    image_base64: Optional[str] = Field(None, description="String base64 da imagem")
    categoria_declarada: Optional[str] = Field(None, example="Buraco na Rua")

class VisualFeaturesDTO(BaseModel):
    brightness: float = Field(..., description="Brilho médio em escala de cinza [0-255]")
    contrast: float = Field(..., description="Contraste médio da imagem [desvio padrão dos pixels]")
    edge_density: float = Field(..., description="Densidade de bordas e gradientes [0-1]")
    texture_roughness: float = Field(..., description="Índice de rugosidade / textura laplaciana [0-1]")
    water_specularity: float = Field(..., description="Reflexo especular indicativo de lâmina d'água [0-1]")
    dominant_color_channel: str = Field(..., description="Canal de cor predominante")

class ImageAnalysisResponse(BaseModel):
    predicted_category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    visual_severity: str = Field(..., description="Baixa | Média | Alta | Crítica")
    category_probabilities: Dict[str, float]
    features: VisualFeaturesDTO
    is_low_quality_warning: bool = False
    warning_message: Optional[str] = None

