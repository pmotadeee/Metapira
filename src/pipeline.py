import os
import logging

try:
    from .security import SecuritySentinel
    from .memory import BM25Memory
    from .skills import SkillManager
    from .llm import DeepSeekClient
except (ImportError, ValueError):
    # Quando concatenado em main.py pelo install.sh, as classes já estão no escopo global
    pass

class CognitivePipeline:
    def __init__(self, config, sentinel, memory, skill_mgr, llm):
        self.config = config
        self.sentinel = sentinel
        self.memory = memory
        self.skill_mgr = skill_mgr
        self.llm = llm

    def load_prompt(self, path: str) -> str:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass
        return ""

    def process_message(self, user_msg: str) -> str:
        # 1. Sentinela de Segurança
        is_safe, safety_msg = self.sentinel.evaluate_message(user_msg, self.llm)
        if not is_safe:
            return safety_msg

        # 2. Recuperação de Memória BM25
        contexto_bm25 = self.memory.search_context(user_msg, top_n=4)

        # 3. Recuperação de Prompts e Tabela Genética de Skills (22 Colunas)
        prompt_roteador = self.load_prompt(self.config.arq_roteador)
        tabela_skills = self.skill_mgr.get_table_markdown()

        system_completo = (
            f"{prompt_roteador}\n\n"
            "====================================================\n"
            "[MATRIZ GENÉTICA DE SKILLS (22 COLUNAS)]\n"
            "====================================================\n"
            f"{tabela_skills}\n"
        )

        user_completo = (
            f"[MEMÓRIAS BM25 RECUPERADAS]\n{contexto_bm25}\n\n"
            f"[MENSAGEM DO USUÁRIO]\n{user_msg}"
        )

        # 4. Inferência Cognitiva
        resposta = self.llm.chat(system_completo, user_completo, temp=0.7)

        # 5. Persistência na Memória de Longo Prazo
        self.memory.save_interaction(user_msg, resposta)

        # 6. Avaliação Evolutiva de Habilidades (IDs 1 a 10, com auto-atualização ao atingir 10)
        try:
            evolucao_resultado = self.skill_mgr.evaluate_and_evolve(user_msg, resposta, self.llm)
            if evolucao_resultado:
                logging.info(f"[EVOLUÇÃO]: {evolucao_resultado}")
        except Exception as e:
            logging.warning(f"Erro no ciclo evolutivo de skills: {e}")

        return resposta
