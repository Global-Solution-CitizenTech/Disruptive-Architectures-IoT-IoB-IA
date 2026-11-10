"""
Módulo de Embeddings Vetoriais Locais e Similaridade de Cosseno — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)

Arquitetura Vetorial:
1. Vetorização Semântica Densa: LocalSemanticEmbedder com projeção estocástica em 512 dimensões e L2-norm.
2. Similaridade de Cosseno Exata com ponderação IDF suavizada.
3. Persistência Vetorial no ChromaDB com métrica de distância 'cosine' em ./data/chroma.
"""
import math
import hashlib
from typing import List, Dict, Optional
from src.utils.text import normalizar_texto, tokenizar_com_ngrams, expansao_semantica_urbana

class LocalSemanticEmbedder:
    """
    Motor local de Embeddings Semânticos Densos para Zeladoria Urbana.
    Gera vetores densos normalizados em R^D (L2-norm = 1.0) para qualquer texto ou query.
    Permite busca vetorial contínua com Similaridade de Cosseno exata sem requerer
    frameworks pesados (PyTorch/TensorFlow) que estourariam o limite de 512 MB de RAM do Render.
    """

    DIMENSAO: int = 512

    @classmethod
    def _hash_termo_para_dimensao(cls, termo: str) -> tuple[int, float]:
        """
        Projeta deterministicamente um termo tokenizado em uma das D dimensões com sinal (+1 ou -1).
        Utiliza Murmur/MD5 hashing para garantir distribuição uniforme e dispersão estocástica.
        """
        h = int(hashlib.md5(termo.encode("utf-8")).hexdigest(), 16)
        indice = h % cls.DIMENSAO
        sinal = 1.0 if ((h >> 8) & 1) == 1 else -1.0
        return indice, sinal

    @classmethod
    def gerar_embedding(cls, texto: str, idf_weights: Dict[str, float] = None) -> List[float]:
        """
        Gera o vetor denso L2-normalizado de DIMENSAO dimensões para o texto fornecido.
        Aplica tokenização, n-grams, expansão semântica urbana e ponderação de frequência.
        """
        if not texto or not texto.strip():
            return [0.0] * cls.DIMENSAO

        texto_limpo = texto[:10000]
        tokens = tokenizar_com_ngrams(texto_limpo, n_max=2)
        tokens_expandidos = expansao_semantica_urbana(tokens)
        
        vetor_denso = [0.0] * cls.DIMENSAO

        if not tokens_expandidos:
            return vetor_denso

        # Frequência de termos e acumulação na projeção densa
        contagem: Dict[str, int] = {}
        for t in tokens_expandidos:
            contagem[t] = contagem.get(t, 0) + 1

        for termo, freq in contagem.items():
            if idf_weights and termo not in idf_weights:
                continue

            peso_idf = idf_weights[termo] if idf_weights else 1.0
            peso_tf = 1.0 + math.log(freq)
            peso_final = peso_tf * peso_idf

            indice, sinal = cls._hash_termo_para_dimensao(termo)
            vetor_denso[indice] += sinal * peso_final

        # Normalização Euclidiana (L2-norm = 1.0) para que o produto escalar seja exatamente o Cosseno
        norma = math.sqrt(sum(x * x for x in vetor_denso))
        if norma > 1e-9:
            return [round(x / norma, 6) for x in vetor_denso]
        return [0.0] * cls.DIMENSAO

def calcular_similaridade_cosseno(vetor_a: List[float], vetor_b: List[float]) -> float:
    """
    Calcula a similaridade de cosseno entre dois vetores normalizados (produto escalar).
    """
    if len(vetor_a) != len(vetor_b) or not vetor_a:
        return 0.0
    return max(0.0, min(1.0, sum(a * b for a, b in zip(vetor_a, vetor_b))))
