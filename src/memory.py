import os
import json
import logging
from datetime import datetime
from rank_bm25 import BM25Okapi

class BM25Memory:
    def __init__(self, history_path: str):
        self.history_path = history_path
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)

    def search_context(self, query: str, top_n: int = 4) -> str:
        if not os.path.exists(self.history_path):
            return "Sem histórico prévio disponível."

        docs = []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            docs.append(f"Usuário: {data.get('user', '')}\nBot: {data.get('bot', '')}")
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logging.warning(f"Erro ao ler histórico de memória: {e}")
            return "Sem histórico disponível."

        if not docs:
            return "Sem histórico prévio."

        tokenized_corpus = [doc.lower().split() for doc in docs]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = query.lower().split()
        top_docs = bm25.get_top_n(tokenized_query, docs, n=min(top_n, len(docs)))

        return "\n---\n".join(top_docs)

    def save_interaction(self, user_msg: str, bot_msg: str):
        try:
            with open(self.history_path, "a", encoding="utf-8") as f:
                log = {
                    "timestamp": datetime.now().isoformat(),
                    "user": user_msg,
                    "bot": bot_msg
                }
                f.write(json.dumps(log, ensure_ascii=False) + "\n")
        except Exception as e:
            logging.error(f"Erro ao salvar interação no histórico: {e}")

    def get_recent_history_text(self, max_chars: int = 5000) -> str:
        if not os.path.exists(self.history_path):
            return ""
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return f.read()[-max_chars:]
        except Exception:
            return ""

    def count_interactions(self) -> int:
        if not os.path.exists(self.history_path):
            return 0
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0
