import logging
import requests

class DeepSeekAPI:
    """
    Classe DeepSeekAPI:
    Gerencia a comunicação HTTP com a API da DeepSeek para
    inferência e auto-evolução cognitiva.
    """
    def __init__(self, key: str, url: str = "https://api.deepseek.com/v1/chat/completions"):
        self.key = key
        self.url = url

    def is_pronta(self) -> bool:
        return bool(self.key and len(self.key) > 5)

    def chamar(self, system_prompt: str, user_prompt: str, temp: float = 0.7) -> str:
        if not self.key:
            return "[ERRO_API]: DEEPSEEK_KEY não configurada no arquivo .env."

        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temp
        }

        try:
            res = requests.post(self.url, headers=headers, json=payload, timeout=60)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"Erro na requisição DeepSeek: {e}")
            return f"[ERRO_DEEPSEEK]: {str(e)}"
