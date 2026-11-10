"""
Testes Unitários do Módulo de Visão Computacional (Aprofundamento 1)
"""

import numpy as np
from PIL import Image
from src.cv.feature_extractor import FeatureExtractor
from src.cv.classifier import UrbanCVClassifier

def test_feature_extractor_synthetic_image():
    # Cria uma imagem sintética cinza com gradiente
    img_arr = np.zeros((256, 256, 3), dtype=np.uint8)
    img_arr[:, :, :] = 128
    # Insere textura e bordas
    img_arr[50:100, 50:100, :] = 250
    img = Image.fromarray(img_arr)

    features, is_low_qual, warning = FeatureExtractor.extract_features(img)
    assert 100.0 < features["brightness"] < 200.0
    assert features["contrast"] > 10.0
    assert "edge_density" in features
    assert "texture_roughness" in features
    assert is_low_qual is False
    assert warning is None

def test_feature_extractor_dark_image_warning():
    # Imagem escura (quase preta)
    img = Image.new("RGB", (256, 256), color=(5, 5, 5))
    features, is_low_qual, warning = FeatureExtractor.extract_features(img)
    assert features["brightness"] < 15.0
    assert is_low_qual is True
    assert "subexposição" in warning.lower()

def test_classifier_training_and_prediction():
    classifier = UrbanCVClassifier()
    assert classifier.is_trained is True

    # Testa predição com features de buraco (alta rugosidade e contraste)
    feat_buraco = {
        "brightness": 120.0,
        "contrast": 75.0,
        "edge_density": 0.50,
        "texture_roughness": 0.85,
        "water_specularity": 0.05,
        "dominant_color_channel": "gray_asphalt"
    }
    pred_cat, conf, probs, sev = classifier.predict_from_features(feat_buraco)
    assert pred_cat in classifier.classes_
    assert 0.0 <= conf <= 1.0
    assert sev in ["Média", "Alta", "Crítica"]

def test_classifier_analyze_without_image():
    classifier = UrbanCVClassifier()
    res = classifier.analyze_image(image_bytes=None, categoria_declarada="Iluminação Pública")
    assert res.predicted_category == "Iluminação Pública"
    assert res.is_low_quality_warning is True

