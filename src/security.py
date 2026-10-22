import logging

class SecuritySentinel:
    def __init__(self, prompt_path: str):
        self.prompt_path = prompt_path

    def load_prompt(self) -> str:
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            logging.warning(f"Não foi possível carregar o prompt de segurança: {e}")
            return ""

    def evaluate_message(self, message: str, llm_client) -> tuple[bool, str]:
        prompt = self.load_prompt()
        if not prompt:
            # Se não houver arquivo de sentinela, aprova por padrão com aviso em log
            return True, "Aprovado (Sentinela sem prompt)"

        resposta = llm_client.chat(prompt, message, temp=0.0)
        if "BLOQUEAR" in resposta.upper():
            return False, "Mensagem bloqueada pelo Sentinela de Segurança do Metapira."
        
        return True, "Aprovado"
