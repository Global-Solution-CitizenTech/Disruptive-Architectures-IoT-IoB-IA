"""
Módulo de Extração de Características Visuais para Imagens Urbanas
Utiliza Pillow e NumPy para análise espectral, gradientes de borda e texturas
"""

import io
import base64
import requests
import numpy as np
from PIL import Image, ImageOps
from typing import Tuple, Dict, Any, Optional

class FeatureExtractor:
    """Extrai descritores visuais de imagens para classificação de zeladoria urbana."""

    @staticmethod
    def load_image(
        image_bytes: Optional[bytes] = None,
        image_base64: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Optional[Image.Image]:
        """Carrega e normaliza uma imagem a partir de bytes, string base64 ou URL."""
        try:
            if image_bytes:
                img = Image.open(io.BytesIO(image_bytes))
            elif image_base64:
                # Remove prefixos data:image/...;base64, se existirem
                if "," in image_base64:
                    image_base64 = image_base64.split(",")[1]
                decoded = base64.b64decode(image_base64)
                img = Image.open(io.BytesIO(decoded))
            elif image_url:
                response = requests.get(image_url, timeout=4.0)
                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content))
                else:
                    return None
            else:
                return None

            # Converte para RGB e redimensiona para tamanho padrão de processamento
            img = img.convert("RGB")
            img = img.resize((256, 256))
            return img
        except Exception as e:
            # Em caso de falha de carregamento ou timeout de rede
            return None

    @classmethod
    def extract_features(cls, image: Image.Image) -> Tuple[Dict[str, Any], bool, Optional[str]]:
        """
        Extrai vetor de características visuais da imagem urbana:
        - Brilho médio
        - Contraste
        - Densidade de bordas (gradiente Sobel aproximado)
        - Rugosidade de textura (variância do Laplaciano)
        - Especularidade de lâmina d'água
        - Canais dominantes de cor
        """
        # Array NumPy RGB [256, 256, 3]
        arr_rgb = np.array(image, dtype=np.float32)
        gray_img = ImageOps.grayscale(image)
        arr_gray = np.array(gray_img, dtype=np.float32)

        # 1. Brilho Médio [0 a 255]
        brightness = float(np.mean(arr_gray))

        # 2. Contraste (Desvio padrão dos pixels em escala de cinza)
        contrast = float(np.std(arr_gray))

        # 3. Gradientes de Borda (Filtros horizontais e verticais de Sobel)
        gx = np.abs(arr_gray[:, 1:] - arr_gray[:, :-1])
        gy = np.abs(arr_gray[1:, :] - arr_gray[:-1, :])
        mean_grad = (np.mean(gx) + np.mean(gy)) / 2.0
        edge_density = float(np.clip(mean_grad / 40.0, 0.0, 1.0))

        # 4. Rugosidade de Textura (Aproximação de Laplaciano discreto 2D)
        # Identifica irregularidades em asfalto quebrado, entulhos e galhos secos
        laplacian = np.abs(
            -4 * arr_gray[1:-1, 1:-1]
            + arr_gray[:-2, 1:-1]
            + arr_gray[2:, 1:-1]
            + arr_gray[1:-1, :-2]
            + arr_gray[1:-1, 2:]
        )
        texture_roughness = float(np.clip(np.mean(laplacian) / 35.0, 0.0, 1.0))

        # 5. Reflexo especular indicativo de lâmina d'água (vazamento ou bueiro entupido)
        # Presença de pixels muito claros (>220) circundados por regiões escuras
        specular_pixels = np.sum(arr_gray > 220) / (256 * 256)
        water_specularity = float(np.clip(specular_pixels * 5.0, 0.0, 1.0))

        # 6. Canais de Cor Predominantes
        mean_r = float(np.mean(arr_rgb[:, :, 0]))
        mean_g = float(np.mean(arr_rgb[:, :, 1]))
        mean_b = float(np.mean(arr_rgb[:, :, 2]))

        if mean_g > mean_r * 1.15 and mean_g > mean_b:
            dominant_color = "green_vegetation"
        elif mean_b > mean_r * 1.15 and mean_b > mean_g:
            dominant_color = "blue_water"
        elif abs(mean_r - mean_g) < 15 and abs(mean_g - mean_b) < 15:
            dominant_color = "gray_asphalt" if brightness > 60 else "pitch_dark"
        elif mean_r > mean_b * 1.25 and mean_r > mean_g:
            dominant_color = "red_rubble_or_sign"
        else:
            dominant_color = "mixed_urban"

        # Detecção de Alerta de Qualidade de Imagem (Casos de Falha)
        is_low_quality = False
        warning = None

        if brightness < 15.0:
            is_low_quality = True
            warning = "Imagem excessivamente escura (subexposição severa). Dificuldade na identificação visual de detalhes."
        elif brightness > 240.0 and contrast < 10.0:
            is_low_quality = True
            warning = "Imagem superexposta (ofuscamento ou saturação branca excessiva)."
        elif contrast < 6.0:
            is_low_quality = True
            warning = "Imagem de baixíssimo contraste ou desfocada."

        features = {
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "edge_density": round(edge_density, 4),
            "texture_roughness": round(texture_roughness, 4),
            "water_specularity": round(water_specularity, 4),
            "dominant_color_channel": dominant_color
        }

        return features, is_low_quality, warning

