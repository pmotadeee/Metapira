#!/bin/bash

# ==========================================================
# METAPIRA - SCRIPT DE INSTALAÇÃO (LINUX / TERMUX)
# ==========================================================

set -e

echo "=============================================="
echo " INICIANDO SETUP DO METAPIRA ENGINE           "
echo "=============================================="

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

# 1. CRIAR A ÁRVORE DE DIRETÓRIOS
echo "[*] Criando árvore de diretórios..."
mkdir -p config/prompts
mkdir -p config/genes
mkdir -p data

# 2. CRIAR ARQUIVOS VAZIOS (Você preenche depois)
echo "[*] Criando arquivos de prompt e tabela (.md) vazios..."
touch config/prompts/seguranca.md
touch config/prompts/roteador.md
touch config/prompts/evolucao.md
touch config/genes/tabela_genetica.md
touch data/historico.jsonl

# 3. CRIAR O requirements.txt
echo "[*] Criando requirements.txt..."
cat << 'EOF' > requirements.txt
python-telegram-bot>=20.7
requests
rank-bm25
EOF

# 4. CRIAR O .env.example
if [ ! -f .env.example ]; then
    echo "[*] Criando .env.example..."
    cat << 'EOF' > .env.example
TELEGRAM_TOKEN=SEU_TOKEN_AQUI
DEEPSEEK_KEY=SUA_CHAVE_AQUI
ADMIN_ID=SEU_ID_TELEGRAM_AQUI
EOF
fi

# 5. CRIAR O main.py (O Monólito)
echo "[*] Criando main.py..."
cat << 'EOF' > main.py
import os
import json
import logging
import shutil
import asyncio
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from rank_bm25 import BM25Okapi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Suporte automático a carregamento de arquivo .env
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# ==========================================
# CONFIGURAÇÕES E CAMINHOS
# ==========================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

ARQ_SEGURANCA = os.path.join(BASE_DIR, "config/prompts/seguranca.md")
ARQ_ROTEADOR = os.path.join(BASE_DIR, "config/prompts/roteador.md")
ARQ_EVOLUCAO = os.path.join(BASE_DIR, "config/prompts/evolucao.md")

ARQ_TABELA = os.path.join(BASE_DIR, "config/genes/tabela_genetica.md")
ARQ_STAGING = os.path.join(BASE_DIR, "config/genes/staging_tabela.md")
ARQ_BACKUP = os.path.join(BASE_DIR, "config/genes/backup_tabela.md")
ARQ_HISTORICO = os.path.join(BASE_DIR, "data/historico.jsonl")

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ==========================================
# I/O E BM25
# ==========================================
def ler_texto(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def buscar_contexto_bm25(query: str, top_n: int = 5) -> str:
    docs = []
    try:
        with open(ARQ_HISTORICO, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                docs.append(f"User: {data['user']} | Bot: {data['bot']}")
    except FileNotFoundError:
        return "Sem histórico."

    if not docs:
        return "Sem histórico."

    tokenized_corpus = [doc.lower().split() for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    
    tokenized_query = query.lower().split()
    top_docs = bm25.get_top_n(tokenized_query, docs, n=top_n)
    
    return "\n---\n".join(top_docs)

def salvar_log(user_msg, bot_msg):
    with open(ARQ_HISTORICO, "a", encoding="utf-8") as f:
        log = {"timestamp": datetime.now().isoformat(), "user": user_msg, "bot": bot_msg}
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

def chamar_deepseek(system_prompt, user_prompt, temp):
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temp
    }
    try:
        res = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERRO_API]: {str(e)}"

# ==========================================
# PIPELINE DE CHAT
# ==========================================
def executar_pipeline(mensagem_usuario):
    prompt_filtro = ler_texto(ARQ_SEGURANCA)
    if not prompt_filtro:
        return "Sistema em manutenção: prompt de segurança ausente."
    
    filtro_res = chamar_deepseek(prompt_filtro, mensagem_usuario, temp=0.0)
    if "BLOQUEAR" in filtro_res.upper():
        return "Mensagem encerrada. Ovelha detectada."

    prompt_roteador = ler_texto(ARQ_ROTEADOR)
    tabela = ler_texto(ARQ_TABELA)
    
    contexto_relevante = buscar_contexto_bm25(mensagem_usuario)
    
    system_completo = f"{prompt_roteador}\n\n[TABELA DE GENES (.MD)]\n{tabela}"
    user_completo = f"[CONTEXTO BM25]\n{contexto_relevante}\n\n[MENSAGEM ATUAL]\n{mensagem_usuario}"
    
    resposta = chamar_deepseek(system_completo, user_completo, temp=0.7)
    salvar_log(mensagem_usuario, resposta)
    return resposta

# ==========================================
# COMANDOS DE ADMIN
# ==========================================
def gerar_evolucao():
    prompt_evo = ler_texto(ARQ_EVOLUCAO)
    tabela = ler_texto(ARQ_TABELA)
    historico_recente = ler_texto(ARQ_HISTORICO)[-5000:]
    
    if not prompt_evo:
        return "[ERRO] Prompt de evolução ausente no arquivo evolucao.md."

    user_prompt = f"[TABELA VIVA (.MD)]\n{tabela}\n\n[HISTÓRICO]\n{historico_recente}"
    nova_tabela = chamar_deepseek(prompt_evo, user_prompt, temp=0.7)
    
    with open(ARQ_STAGING, "w", encoding="utf-8") as f:
        f.write(nova_tabela)
    return "Patch de evolução gerado em staging_tabela.md. Use /deploy para aprovar."

def fazer_deploy():
    if not os.path.exists(ARQ_STAGING):
        return "Nenhum staging pendente."
    
    shutil.copy(ARQ_TABELA, ARQ_BACKUP)
    shutil.move(ARQ_STAGING, ARQ_TABELA)
    return "Deploy concluído. Tabela Genética atualizada."

def fazer_rollback():
    if not os.path.exists(ARQ_BACKUP):
        return "Nenhum backup disponível."
    shutil.copy(ARQ_BACKUP, ARQ_TABELA)
    return "Rollback executado. Tabela restaurada."

# ==========================================
# HANDLERS TELEGRAM
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Metapira Linux Engine online.")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    res = await asyncio.to_thread(executar_pipeline, update.message.text)
    await update.message.reply_text(res)

async def cmd_evolve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text("⏳ Evoluindo tabela genética via LLM...")
    res = await asyncio.to_thread(gerar_evolucao)
    await update.message.reply_text(res)

async def cmd_deploy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    res = fazer_deploy()
    await update.message.reply_text(res)

async def cmd_rollback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    res = fazer_rollback()
    await update.message.reply_text(res)

def main():
    if not TELEGRAM_TOKEN:
        logging.error("ERRO: TELEGRAM_TOKEN não configurado! Defina a variável de ambiente ou configure o arquivo .env.")
        return
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    app.add_handler(CommandHandler("evolve", cmd_evolve))
    app.add_handler(CommandHandler("deploy", cmd_deploy))
    app.add_handler(CommandHandler("rollback", cmd_rollback))
    
    logging.info("Kernel rodando em produção Linux. Aguardando eventos...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
EOF

# 6. CRIAR O ARQUIVO SYSTEMD (metapira.service)
echo "[*] Criando arquivo de serviço systemd (metapira.service)..."
cat << 'EOF' > metapira.service
[Unit]
Description=Metapira Cognitive Engine
After=network.target

[Service]
Type=simple
User=SEU_USUARIO_AQUI
WorkingDirectory=/home/SEU_USUARIO_AQUI/metapira
Environment="TELEGRAM_TOKEN=SEU_TOKEN_AQUI"
Environment="DEEPSEEK_KEY=SUA_CHAVE_AQUI"
Environment="ADMIN_ID=SEU_ID_TELEGRAM_AQUI"
ExecStart=/home/SEU_USUARIO_AQUI/metapira/venv/bin/python /home/SEU_USUARIO_AQUI/metapira/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 7. CRIAR O SCRIPT DE EXECUÇÃO LOCAL / TERMUX (run.sh)
echo "[*] Criando script de execução local (run.sh)..."
cat << 'EOF' > run.sh
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
EOF
chmod +x run.sh

# 8. INSTALAR DEPENDÊNCIAS
echo "[*] Criando ambiente virtual e instalando dependências..."
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt

echo "=============================================="
echo " SETUP CONCLUÍDO COM SUCESSO!                 "
echo "=============================================="
echo "Próximos passos:"
echo "1. Edite os arquivos na pasta 'config/prompts/' com seus prompts."
echo "2. Edite o arquivo 'config/genes/tabela_genetica.md' com a sua tabela."
echo "3. Copie .env.example para .env e preencha suas chaves (ou edite o metapira.service)."
echo "4. No Termux, rode './run.sh' para iniciar o bot."
echo "=============================================="
