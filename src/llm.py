import requests
import logging

class DeepSeekClient:
    def __init__(self, api_key: str, api_url: str = "https://api.deepseek.com/v1/chat/completions", timeout: int = 60):
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("sk-"))

    def chat(self, system_prompt: str, user_prompt: str, temp: float = 0.7) -> str:
        if not self.api_key:
            return "[ERRO_CONFIG]: Chave DEEPSEEK_KEY ausente ou não configurada."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
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
            res = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na requisição DeepSeek: {e}")
            return f"[ERRO_DEEPSEEK]: {str(e)}"
