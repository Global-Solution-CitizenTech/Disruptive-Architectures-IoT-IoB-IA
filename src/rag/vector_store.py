"""
Vector Store em Memória para RAG de Legislação e Zeladoria Urbana
Utiliza TF-IDF com n-gramas e Similaridade de Cosseno da Scikit-Learn
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..config import KNOWLEDGE_BASE_DIR, RAG_TOP_K, RAG_SIMILARITY_THRESHOLD
from ..schemas.rag_models import RagDocumentChunk

DOC_CATEGORY_MAPPING = {
    "regulamento_pavimentacao_tapa_buraco": ["Buraco na Rua", "Tapa-Buraco", "Pavimentação", "Asfalto", "Cratera", "Via pública", "Subprefeitura Pavimentação"],
    "manual_drenagem_bueiros_alagamentos": ["Bueiro Entupido", "Boca de Lobo", "Drenagem", "Hidrojato", "Hidrojateamento", "Alagamento", "Sarjeta", "Águas Pluviais"],
    "norma_iluminacao_publica_led": ["Iluminação Pública", "Poste Apagado", "Lâmpada LED", "Ponto Escuro", "Ilumina SP", "Luminária", "Fiação"],
    "codigo_limpeza_urbana_residuos": ["Entulho e Descarte Irregular", "Limpeza Urbana", "Lixo", "Entulho", "Resíduos", "Ecoponto", "Calçada"],
    "manual_manejo_arboreo_defesa_civil": ["Poda de Árvore", "Árvore", "Galho", "Manejo Arbóreo", "Fiação Elétrica", "Defesa Civil", "Motosserra"],
    "diretrizes_sinalizacao_cet": ["Sinalização e Trânsito", "Semáforo", "Faixa de Pedestres", "Placa", "CET", "Cruzamento", "Trânsito"],
    "concessionaria_saneamento_sabesp": ["Vazamento de Água", "Cano Quebrado", "Adutora", "Saneamento", "Sabesp", "Água"]
}

class RagVectorStore:
    """Indexador vetorial para recuperação semântica de normas de zeladoria urbana."""

    def __init__(self, kb_dir: Optional[Path] = None):
        self.kb_dir = kb_dir or KNOWLEDGE_BASE_DIR
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_df=0.95,
            min_df=1,
            sublinear_tf=True
        )
        self.tfidf_matrix = None
        self._load_and_index_documents()

    def _extract_metadata_from_doc(self, text: str) -> Dict[str, Any]:
        """Extrai metadados do cabeçalho do documento normativo."""
        base_legal = None
        orgao = None

        m_legal = re.search(r"\*\*Base Legal:\*\*\s*(.+)", text)
        if m_legal:
            base_legal = m_legal.group(1).strip()

        m_orgao = re.search(r"\*\*Órgão Responsável:\*\*\s*(.+)", text)
        if m_orgao:
            orgao = m_orgao.group(1).strip()

        return {"base_legal": base_legal, "orgao": orgao}

    def _extract_sla_from_chunk(self, chunk_text: str) -> Optional[int]:
        """Identifica prazos de SLA mencionados no texto do chunk."""
        m = re.search(r"(\d+)\s*horas?", chunk_text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        m_dias = re.search(r"(\d+)\s*dias?", chunk_text, re.IGNORECASE)
        if m_dias:
            return int(m_dias.group(1)) * 24
        return None

    def _load_and_index_documents(self):
        """Lê os arquivos markdown, divide em chunks semânticos e indexa."""
        if not self.kb_dir.exists():
            return

        self.chunks.clear()
        doc_files = list(self.kb_dir.glob("*.md"))

        corpus = []

        for fpath in doc_files:
            try:
                content = fpath.read_text(encoding="utf-8")
                metadata = self._extract_metadata_from_doc(content)
                cat_keywords = " ".join(DOC_CATEGORY_MAPPING.get(fpath.stem, []))

                # Divide o documento por seções ##
                sections = re.split(r"\n(?=##\s+)", content)
                doc_title = sections[0].split("\n")[0].replace("#", "").strip()

                for s_idx, sec in enumerate(sections):
                    cleaned_sec = sec.strip()
                    if not cleaned_sec:
                        continue

                    sec_title = cleaned_sec.split("\n")[0].replace("#", "").strip()
                    sla_hours = self._extract_sla_from_chunk(cleaned_sec)
                    chunk_id = f"{fpath.stem}_chk_{s_idx}"

                    # Enriquecimento com as palavras-chave da categoria associada
                    searchable_text = f"{doc_title} {sec_title} {cat_keywords} {cleaned_sec} {metadata.get('base_legal', '')}"

                    chunk_obj = {
                        "chunk_id": chunk_id,
                        "source_file": fpath.name,
                        "doc_stem": fpath.stem,
                        "title": f"{doc_title} - {sec_title}",
                        "content": cleaned_sec,
                        "law_article": metadata.get("base_legal"),
                        "competent_agency": metadata.get("orgao"),
                        "sla_hours": sla_hours,
                        "searchable_text": searchable_text
                    }

                    self.chunks.append(chunk_obj)
                    corpus.append(searchable_text)
            except Exception:
                continue

        if corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search(
        self,
        query: str,
        category_hint: Optional[str] = None,
        top_k: int = RAG_TOP_K
    ) -> List[RagDocumentChunk]:
        """Realiza busca vetorial semântica e retorna os chunks mais similares com ranking."""
        if not self.chunks or self.tfidf_matrix is None:
            return []

        # Expansão contextual com categoria
        expanded_query = query
        if category_hint:
            expanded_query = f"{category_hint} {category_hint} {query}"

        query_vec = self.vectorizer.transform([expanded_query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0].copy()

        # Boost se o chunk pertencer explicitamente à categoria indicada
        if category_hint:
            for idx, chk in enumerate(self.chunks):
                stem = chk.get("doc_stem", "")
                mapped_terms = DOC_CATEGORY_MAPPING.get(stem, [])
                if any(category_hint.lower() in term.lower() for term in mapped_terms):
                    similarities[idx] += 0.35

        ranked_indices = np.argsort(similarities)[::-1]

        results: List[RagDocumentChunk] = []
        for idx in ranked_indices[:top_k]:
            score = float(similarities[idx])
            c = self.chunks[idx]

            results.append(
                RagDocumentChunk(
                    chunk_id=c["chunk_id"],
                    source_file=c["source_file"],
                    title=c["title"],
                    content=c["content"],
                    law_article=c["law_article"],
                    sla_hours=c["sla_hours"],
                    competent_agency=c["competent_agency"],
                    similarity_score=round(score, 4)
                )
            )

        return results
