"""
Teste de Cobertura da Base de Conhecimento RAG: ZelaFix AI
Valida que cada pergunta de munícipe sobre zeladoria urbana recupera o chunk esperado
entre os 2 primeiros resultados, e perguntas fora de escopo não recuperam nada.
Uso: python test_knowledge_coverage.py (executar dentro de deploy_zelafixai_render)
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import sys
import os

DIRETORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRETORIO_RAIZ)

from src.knowledge import BASE_CHUNKS_RAG
from src.services.knowledge_service import KnowledgeService

CASOS = [
    # Pavimentação e Tapa-Buraco
    ("Tem um buraco enorme na rua quebrando a suspensão dos carros", "pav_01"),
    ("Qual o prazo que a prefeitura tem para tapar buraco no asfalto?", "pav_02"),
    ("Abriu uma cratera profunda no meio da avenida com risco de acidente", "pav_03"),
    ("A Sabesp abriu uma vala na rua e não fechou direito o asfalto", "pav_04"),
    ("A rua inteira está esburacada e precisa de recapeamento novo", "pav_05"),

    # Drenagem, Bueiros e Enchentes
    ("O bueiro da minha rua está entupido de terra e folhas", "dren_01"),
    ("Boca de lobo transbordando água e com risco de enchente no bairro", "dren_02"),
    ("Roubaram a tampa de ferro do bueiro e alguém pode cair dentro", "dren_03"),
    ("A calçada está afundando perto da galeria de água pluvial", "dren_04"),

    # Iluminação Pública
    ("O poste em frente da minha casa está com a lâmpada apagada", "ilum_01"),
    ("Vários postes apagados perto do ponto de ônibus e da escola", "ilum_02"),
    ("A lâmpada do poste fica acesa direto durante o dia", "ilum_03"),
    ("Um carro bateu no poste e tem fio desencapado no chão", "ilum_04"),

    # Limpeza Urbana, Resíduos e Ecopontos
    ("Onde posso jogar entulho de obra e quanto custa no ecoponto?", "limp_01"),
    ("Jogaram entulho e lixo na calçada e estão sujando a rua", "limp_02"),
    ("Quando passa o caminhão do cata-bagulho para levar meu sofá velho?", "limp_03"),
    ("Tem um terreno baldio abandonado cheio de lixo e foco de dengue", "limp_04"),

    # Manejo Arbóreo
    ("Preciso pedir a poda de uma árvore alta na calçada", "arb_01"),
    ("Os galhos da árvore estão encostando nos fios elétricos e dando faísca", "arb_02"),
    ("A árvore está com o tronco oco e inclinada quase caindo na casa", "arb_03"),
    ("Caiu uma árvore no meio da rua depois da tempestade de ontem", "arb_04"),

    # Sinalização e Trânsito (CET)
    ("O semáforo do cruzamento está apagado e vai dar batida de carro", "cet_01"),
    ("Arrancaram a placa de Pare da esquina e ninguém sabe a preferência", "cet_02"),
    ("A faixa de pedestres em frente à escola está totalmente apagada", "cet_03"),

    # Saneamento Básico (Sabesp)
    ("Cano quebrado da Sabesp jorrando água limpa na rua", "sab_01"),
    ("Tem esgoto a céu aberto vazando com cheiro horrível na sarjeta", "sab_02"),
    ("O hidrômetro do cavalete de água está com vazamento", "sab_03"),

    # Direitos do Cidadão, Acessibilidade e App
    ("Como funciona o aplicativo ZelaFix para abrir chamados?", "faq_01"),
    ("Para que servem os apoios comunitários de vizinhos no chamado?", "faq_02"),
    ("Quem é obrigado a arrumar a calçada esburacada para cadeirante?", "faq_03"),
    ("A prefeitura não cumpriu o prazo do chamado, onde reclamo na ouvidoria?", "faq_04"),

    # Casos Fora de Escopo (Esperado: None / sem chunks)
    ("qual a capital da França", None),
    ("receita de bolo de cenoura com chocolate", None),
    ("escreva uma função em Python para ordenar lista", None),
    ("quem ganhou o campeonato brasileiro de futebol", None),
]

def main() -> int:
    ids = [c["id"] for c in BASE_CHUNKS_RAG]
    assert len(ids) == len(set(ids)), f"IDs de chunk duplicados: {len(ids)} vs {len(set(ids))}"
    obrigatorios = {"id", "source", "category", "title", "content", "keywords"}
    assert all(obrigatorios <= c.keys() for c in BASE_CHUNKS_RAG), "Chunk sem campos obrigatórios"

    falhas = 0
    print(f"\n🚀 Iniciando Teste de Cobertura da Base RAG ZelaFix ({len(BASE_CHUNKS_RAG)} chunks indexados)...")
    print("-" * 80)

    for pergunta, esperado in CASOS:
        resultado = KnowledgeService.buscar_chunks_rag(pergunta, top_k=3)
        topo = [c["id"] for c in resultado["chunks"]]
        
        if esperado is None:
            ok = len(topo) == 0
        else:
            ok = esperado in topo[:2]

        status = "✅ OK" if ok else "❌ FALHA"
        esperado_str = str(esperado) if esperado else "None"
        print(f"{status} | {pergunta[:50]:<50} -> {topo[:2]} (esperado: {esperado_str})")
        if not ok:
            falhas += 1

    print("-" * 80)
    total = len(CASOS)
    aprovados = total - falhas
    taxa = (aprovados / total) * 100
    print(f"Resultado Final: {aprovados}/{total} casos aprovados ({taxa:.1f}% de precisão).")
    
    if falhas == 0:
        print("🎉 TODOS OS TESTES DE COBERTURA PASSARAM COM SUCESSO!\n")
        return 0
    else:
        print(f"⚠️ Ocorreram {falhas} falhas na recuperação semântica.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
