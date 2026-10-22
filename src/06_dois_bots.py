import os
import logging

class SentinelaBot:
    """
    Bot 1 (Instância Sentinela):
    Primeira linha de defesa. Analisa a mensagem com temperatura zero
    e classifica a entrada para barrar prompt injections ou ataques.
    """
    def __init__(self, caminho_prompt: str, api_deepseek):
        self.caminho_prompt = caminho_prompt
        self.api = api_deepseek

    def ler_prompt(self) -> str:
        if os.path.exists(self.caminho_prompt):
            try:
                with open(self.caminho_prompt, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass
        return ""

    def filtrar(self, mensagem_usuario: str) -> tuple[bool, str]:
        prompt = self.ler_prompt()
        if not prompt:
            return True, "Aprovado (Sem prompt sentinela)"

        resultado = self.api.chamar(prompt, mensagem_usuario, temp=0.0)
        if "BLOQUEAR" in resultado.upper():
            return False, "Mensagem bloqueada pelo Sentinela de Segurança do Metapira."

        return True, "Aprovado"


class RoteadorBot:
    """
    Bot 2 (Instância Roteador / Persona Cognitiva):
    Segunda linha do processamento. Formula a resposta inteligente
    integrando a persona, a Tabela de Skills de 22 colunas e as memórias BM25.
    """
    def __init__(self, caminho_prompt: str, api_deepseek, tabela_skills, memoria):
        self.caminho_prompt = caminho_prompt
        self.api = api_deepseek
        self.tabela_skills = tabela_skills
        self.memoria = memoria

    def ler_prompt(self) -> str:
        if os.path.exists(self.caminho_prompt):
            try:
                with open(self.caminho_prompt, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass
        return ""

    def processar(self, usuario, mensagem_usuario: str) -> str:
        prompt_roteador = self.ler_prompt()
        contexto_bm25 = self.memoria.buscar_contexto(mensagem_usuario, top_n=4)
        tabela_md = self.tabela_skills.obter_markdown()

        # Identificação de usuário se disponível
        tag_user = f"@{usuario.username}" if getattr(usuario, "username", None) else getattr(usuario, "nome", "Usuário")

        system_completo = (
            f"{prompt_roteador}\n\n"
            "====================================================\n"
            "[MATRIZ GENÉTICA DE SKILLS (22 COLUNAS)]\n"
            "====================================================\n"
            f"{tabela_md}\n"
        )

        user_completo = (
            f"[MEMÓRIAS RELEVANTES BM25]\n{contexto_bm25}\n\n"
            f"[USUÁRIO ATUAL: {tag_user}]\n"
            f"[MENSAGEM]: {mensagem_usuario}"
        )

        resposta = self.api.chamar(system_completo, user_completo, temp=0.7)
        self.memoria.salvar(mensagem_usuario, resposta)

        # Avaliação de evolução dinâmica de skills (1 a 10 IDs)
        try:
            self.tabela_skills.avaliar_e_evoluir(mensagem_usuario, resposta, self.api)
        except Exception as e:
            logging.warning(f"Erro no ciclo evolutivo de skills: {e}")

        return resposta
