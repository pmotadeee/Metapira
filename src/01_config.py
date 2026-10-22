import os

class Config:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            if not os.path.exists(os.path.join(base_dir, "config")):
                base_dir = os.path.dirname(base_dir)

        self.base_dir = base_dir
        self.carregar_env()

        self.telegram_token = os.getenv("TELEGRAM_TOKEN", "").strip()
        self.deepseek_key = os.getenv("DEEPSEEK_KEY", "").strip()
        admin_id_str = os.getenv("ADMIN_ID", "0").strip()
        self.admin_id = int(admin_id_str) if admin_id_str.isdigit() else 0
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"

        # Caminhos dos Prompts e Genes
        self.arq_seguranca = os.path.join(self.base_dir, "config/prompts/seguranca.md")
        self.arq_roteador = os.path.join(self.base_dir, "config/prompts/roteador.md")
        self.arq_evolucao = os.path.join(self.base_dir, "config/prompts/evolucao.md")
        self.arq_tabela = os.path.join(self.base_dir, "config/genes/tabela_genetica.md")
        self.arq_staging = os.path.join(self.base_dir, "config/genes/staging_tabela.md")
        self.arq_backup = os.path.join(self.base_dir, "config/genes/backup_tabela.md")
        self.arq_historico = os.path.join(self.base_dir, "data/historico.jsonl")

    def carregar_env(self):
        env_path = os.path.join(self.base_dir, ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            except Exception:
                pass
