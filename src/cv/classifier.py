"""
Classificador Supervisionado de Imagens Urbanas com Scikit-Learn
Utiliza Random Forest treinado sobre vetores de características visuais
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from PIL import Image

from ..config import DATASET_DIR, CATEGORIAS_OFICIAIS
from .feature_extractor import FeatureExtractor
from ..schemas.cv_models import ImageAnalysisResponse, VisualFeaturesDTO

class UrbanCVClassifier:
    """Classificador de ocorrências de zeladoria urbana baseado em visão computacional."""

    def __init__(self, dataset_path: Optional[Path] = None):
        self.dataset_path = dataset_path or (DATASET_DIR / "samples.json")
        self.scaler = StandardScaler()
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            class_weight="balanced"
        )
        self.classes_ = CATEGORIAS_OFICIAIS
        self.is_trained = False
        self._train_from_dataset()

    def _feature_dict_to_vector(self, feat: Dict[str, Any]) -> np.ndarray:
        """Converte dicionário de features em vetor numérico de 5 dimensões."""
        return np.array([
            float(feat.get("brightness", 120.0)),
            float(feat.get("contrast", 50.0)),
            float(feat.get("edge_density", 0.3)),
            float(feat.get("texture_roughness", 0.5)),
            float(feat.get("water_specularity", 0.1))
        ], dtype=np.float32)

    def _train_from_dataset(self):
        """Treina o modelo nos dados sintéticos e rotulados do ZelaFix."""
        if not self.dataset_path.exists():
            # Fallback caso dataset ainda não tenha sido gerado
            self.is_trained = False
            return

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            samples = json.load(f)

        X = []
        y = []
        for s in samples:
            if s.get("is_failure_case", False):
                continue
            cat = s.get("categoria", "Outros")
            if cat not in self.classes_:
                cat = "Outros"
            vf = s.get("visual_features", {})
            vec = self._feature_dict_to_vector(vf)
            X.append(vec)
            y.append(cat)

        if len(X) < 10:
            return

        X_arr = np.array(X)
        self.scaler.fit(X_arr)
        X_scaled = self.scaler.transform(X_arr)

        self.model.fit(X_scaled, y)
        self.classes_ = list(self.model.classes_)
        self.is_trained = True

    def predict_from_features(self, feat: Dict[str, Any]) -> Tuple[str, float, Dict[str, float], str]:
        """Classifica a partir do dicionário de características visuais extraídas."""
        vec = self._feature_dict_to_vector(feat).reshape(1, -1)
        
        if self.is_trained:
            vec_scaled = self.scaler.transform(vec)
            pred_class = self.model.predict(vec_scaled)[0]
            probs = self.model.predict_proba(vec_scaled)[0]
            prob_dict = {cls_name: round(float(p), 4) for cls_name, p in zip(self.classes_, probs)}
            confidence = float(np.max(probs))
        else:
            # Fallback heurístico inteligente
            pred_class, confidence, prob_dict = self._heuristic_classification(feat)

        # Determina a severidade visual estimada
        severity = self._estimate_visual_severity(feat, pred_class)
        return pred_class, round(confidence, 4), prob_dict, severity

    def _heuristic_classification(self, feat: Dict[str, Any]) -> Tuple[str, float, Dict[str, float]]:
        """Fallback heurístico caso modelo não esteja treinado."""
        b = feat.get("brightness", 120.0)
        ws = feat.get("water_specularity", 0.0)
        tr = feat.get("texture_roughness", 0.0)
        ed = feat.get("edge_density", 0.0)
        dom = feat.get("dominant_color_channel", "")

        prob_dict = {cat: 0.05 for cat in CATEGORIAS_OFICIAIS}

        if b < 30.0:
            pred = "Iluminação Pública"
            prob_dict["Iluminação Pública"] = 0.85
        elif ws > 0.4:
            pred = "Vazamento de Água" if ws > 0.7 else "Bueiro Entupido"
            prob_dict[pred] = 0.80
        elif dom == "green_vegetation":
            pred = "Poda de Árvore"
            prob_dict["Poda de Árvore"] = 0.82
        elif tr > 0.6 and ed > 0.4:
            pred = "Buraco na Rua"
            prob_dict["Buraco na Rua"] = 0.78
        elif tr > 0.5:
            pred = "Entulho e Descarte Irregular"
            prob_dict["Entulho e Descarte Irregular"] = 0.70
        else:
            pred = "Outros"
            prob_dict["Outros"] = 0.50

        return pred, prob_dict[pred], prob_dict

    def _estimate_visual_severity(self, feat: Dict[str, Any], category: str) -> str:
        """Estima a severidade visual do dano com base nas características da imagem."""
        b = feat.get("brightness", 120.0)
        tr = feat.get("texture_roughness", 0.0)
        ed = feat.get("edge_density", 0.0)
        ws = feat.get("water_specularity", 0.0)

        # Regras de engenharia visual urbana
        if category == "Iluminação Pública" and b < 25.0:
            return "Crítica"
        if category == "Buraco na Rua" and (tr > 0.75 or ed > 0.65):
            return "Crítica"
        if category in ["Vazamento de Água", "Bueiro Entupido"] and ws > 0.60:
            return "Crítica"
        if category == "Entulho e Descarte Irregular" and (tr > 0.70 and ed > 0.55):
            return "Alta"
        if category == "Poda de Árvore" and (ed > 0.55 and tr > 0.65):
            return "Alta"

        if tr > 0.40 or ed > 0.35:
            return "Média"
        return "Baixa"

    def analyze_image(
        self,
        image_bytes: Optional[bytes] = None,
        image_base64: Optional[str] = None,
        image_url: Optional[str] = None,
        categoria_declarada: Optional[str] = None
    ) -> ImageAnalysisResponse:
        """Executa o pipeline completo de visão computacional em uma imagem."""
        img = FeatureExtractor.load_image(
            image_bytes=image_bytes,
            image_base64=image_base64,
            image_url=image_url
        )

        if img is None:
            # Em caso de imagem ausente ou corrompida, retorna análise neutra com aviso
            features = {
                "brightness": 128.0,
                "contrast": 50.0,
                "edge_density": 0.25,
                "texture_roughness": 0.30,
                "water_specularity": 0.0,
                "dominant_color_channel": "unknown"
            }
            return ImageAnalysisResponse(
                predicted_category=categoria_declarada or "Outros",
                confidence=0.50,
                visual_severity="Média",
                category_probabilities={cat: 0.125 for cat in CATEGORIAS_OFICIAIS},
                features=VisualFeaturesDTO(**features),
                is_low_quality_warning=True,
                warning_message="Não foi possível processar a imagem (URL indisponível ou bytes inválidos). Triagem prosseguiu por texto e telemetria."
            )

        features, is_low_qual, warning = FeatureExtractor.extract_features(img)
        pred_cat, conf, probs, severity = self.predict_from_features(features)

        # Se o usuário declarou uma categoria válida e a imagem não foi discrepante, pondera
        if categoria_declarada and categoria_declarada in CATEGORIAS_OFICIAIS:
            if probs.get(categoria_declarada, 0.0) > 0.20:
                pred_cat = categoria_declarada

        return ImageAnalysisResponse(
            predicted_category=pred_cat,
            confidence=conf,
            visual_severity=severity,
            category_probabilities=probs,
            features=VisualFeaturesDTO(**features),
            is_low_quality_warning=is_low_qual,
            warning_message=warning
        )

