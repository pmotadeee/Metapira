import os
from dataclasses import dataclass

@dataclass
class Config:
    base_dir: str
    telegram_token: str
    deepseek_key: str
    admin_id: int
    deepseek_url: str = "https://api.deepseek.com/v1/chat/completions"
    
    # Arquivos de Prompts e Genes
    arq_seguranca: str = ""
    arq_roteador: str = ""
    arq_evolucao: str = ""
    arq_tabela: str = ""
    arq_staging: str = ""
    arq_backup: str = ""
    arq_historico: str = ""

    @classmethod
    def load(cls, base_dir: str = None) -> "Config":
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if not os.path.exists(os.path.join(base_dir, "config")):
                # Caso esteja rodando a partir do monólito na raiz
                base_dir = os.path.dirname(os.path.abspath(__file__))

        env_file = os.path.join(base_dir, ".env")
        if os.path.exists(env_file):
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            except Exception:
                pass

        token = os.getenv("TELEGRAM_TOKEN", "").strip()
        ds_key = os.getenv("DEEPSEEK_KEY", "").strip()
        admin_id_str = os.getenv("ADMIN_ID", "0").strip()
        admin_id = int(admin_id_str) if admin_id_str.isdigit() else 0

        return cls(
            base_dir=base_dir,
            telegram_token=token,
            deepseek_key=ds_key,
            admin_id=admin_id,
            arq_seguranca=os.path.join(base_dir, "config/prompts/seguranca.md"),
            arq_roteador=os.path.join(base_dir, "config/prompts/roteador.md"),
            arq_evolucao=os.path.join(base_dir, "config/prompts/evolucao.md"),
            arq_tabela=os.path.join(base_dir, "config/genes/tabela_genetica.md"),
            arq_staging=os.path.join(base_dir, "config/genes/staging_tabela.md"),
            arq_backup=os.path.join(base_dir, "config/genes/backup_tabela.md"),
            arq_historico=os.path.join(base_dir, "data/historico.jsonl")
        )
