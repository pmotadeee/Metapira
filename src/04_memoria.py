import os
import json
import logging
from datetime import datetime
from rank_bm25 import BM25Okapi

class MemoriaBM25:
    """
    Classe MemoriaBM25:
    Armazena o histórico em JSON Lines e realiza busca de contexto
    relevante com tokenização e ranking Okapi BM25.
    """
    def __init__(self, caminho_historico: str):
        self.caminho_historico = caminho_historico
        os.makedirs(os.path.dirname(self.caminho_historico), exist_ok=True)

    def buscar_contexto(self, query: str, top_n: int = 4) -> str:
        if not os.path.exists(self.caminho_historico):
            return "Sem histórico prévio disponível."

        docs = []
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            d = json.loads(line)
                            docs.append(f"Usuário: {d.get('user', '')}\nBot: {d.get('bot', '')}")
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logging.warning(f"Erro ao ler histórico: {e}")
            return "Sem histórico disponível."

        if not docs:
            return "Sem histórico prévio."

        corpus = [doc.lower().split() for doc in docs]
        bm25 = BM25Okapi(corpus)
        top = bm25.get_top_n(query.lower().split(), docs, n=min(top_n, len(docs)))
        return "\n---\n".join(top)

    def salvar(self, user_msg: str, bot_msg: str):
        try:
            with open(self.caminho_historico, "a", encoding="utf-8") as f:
                registro = {
                    "timestamp": datetime.now().isoformat(),
                    "user": user_msg,
                    "bot": bot_msg
                }
                f.write(json.dumps(registro, ensure_ascii=False) + "\n")
        except Exception as e:
            logging.error(f"Erro ao salvar histórico: {e}")

    def contar_registros(self) -> int:
        if not os.path.exists(self.caminho_historico):
            return 0
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0
