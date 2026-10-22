# ==============================================================================
# METAPIRA COGNITIVE ENGINE - MONÓLITO AUTO-CONCATENADO
# Arquitetura: OOP Modularizada -> Monólito Final via install.sh
# ==============================================================================

# ==============================================================================
# MÓDULO CONCATENADO: src/config.py
# ==============================================================================
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

# ==============================================================================
# MÓDULO CONCATENADO: src/security.py
# ==============================================================================
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

# ==============================================================================
# MÓDULO CONCATENADO: src/memory.py
# ==============================================================================
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

# ==============================================================================
# MÓDULO CONCATENADO: src/skills.py
# ==============================================================================
import os
import re
import shutil
import logging
from dataclasses import dataclass, field
from typing import List, Optional

COLUMNS_22 = [
    "ID", "Layer1_Style", "ENTITY", "Impact", "Layer2_Archetype",
    "Layer3_Domain", "Layer4_Valence", "Layer5_Strategy", "Influence_Weight",
    "Conflict_Status", "Activation_Phrase_1", "Activation_Phrase_2",
    "Activation_Phrase_3", "Activation_Phrase_4", "Activation_Phrase_5",
    "Activation_Phrase_6", "Activation_Phrase_7", "Activation_Phrase_8",
    "Activation_Phrase_9", "Activation_Phrase_10", "Activation_Phrase_11",
    "Activation_Phrase_12"
]

@dataclass
class SkillGene:
    id: int
    layer1_style: str
    entity: str
    impact: str
    layer2_archetype: str
    layer3_domain: str
    layer4_valence: str
    layer5_strategy: str
    influence_weight: str
    conflict_status: str
    activation_phrases: List[str] = field(default_factory=lambda: [""] * 12)

    def to_markdown_row(self) -> str:
        phrases = self.activation_phrases + [""] * (12 - len(self.activation_phrases))
        phrases = phrases[:12]
        fields = [
            str(self.id),
            self.layer1_style.strip(),
            self.entity.strip(),
            self.impact.strip(),
            self.layer2_archetype.strip(),
            self.layer3_domain.strip(),
            self.layer4_valence.strip(),
            self.layer5_strategy.strip(),
            self.influence_weight.strip(),
            self.conflict_status.strip()
        ] + [p.strip() for p in phrases]
        return "| " + " | ".join(fields) + " |"

    @classmethod
    def from_markdown_row(cls, row_str: str) -> Optional["SkillGene"]:
        parts = [p.strip() for p in row_str.strip().strip("|").split("|")]
        if len(parts) < 10:
            return None
        
        try:
            skill_id = int(re.sub(r"[^\d]", "", parts[0]))
        except ValueError:
            return None

        phrases = parts[10:22]
        while len(phrases) < 12:
            phrases.append("")
        
        return cls(
            id=skill_id,
            layer1_style=parts[1] if len(parts) > 1 else "Direto",
            entity=parts[2] if len(parts) > 2 else "Metapira",
            impact=parts[3] if len(parts) > 3 else "Base",
            layer2_archetype=parts[4] if len(parts) > 4 else "Executor",
            layer3_domain=parts[5] if len(parts) > 5 else "Geral",
            layer4_valence=parts[6] if len(parts) > 6 else "Neutra",
            layer5_strategy=parts[7] if len(parts) > 7 else "Heurística",
            influence_weight=parts[8] if len(parts) > 8 else "0.5",
            conflict_status=parts[9] if len(parts) > 9 else "Alinhado",
            activation_phrases=phrases[:12]
        )

class SkillManager:
    MAX_SKILLS = 10

    def __init__(self, table_path: str, staging_path: str = "", backup_path: str = ""):
        self.table_path = table_path
        self.staging_path = staging_path or table_path.replace(".md", "_staging.md")
        self.backup_path = backup_path or table_path.replace(".md", "_backup.md")
        os.makedirs(os.path.dirname(self.table_path), exist_ok=True)

    def load_skills(self) -> List[SkillGene]:
        skills = []
        if not os.path.exists(self.table_path):
            return skills

        try:
            with open(self.table_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("|") and not ("---" in line) and not ("Layer1_Style" in line):
                        gene = SkillGene.from_markdown_row(line)
                        if gene:
                            skills.append(gene)
        except Exception as e:
            logging.error(f"Erro ao carregar genes da tabela: {e}")

        # Ordenar por ID
        skills.sort(key=lambda s: s.id)
        return skills[:self.MAX_SKILLS]

    def save_skills(self, skills: List[SkillGene], target_file: str = None) -> bool:
        dest = target_file or self.table_path
        skills.sort(key=lambda s: s.id)
        skills = skills[:self.MAX_SKILLS]

        header = "| " + " | ".join(COLUMNS_22) + " |"
        sep = "| " + " | ".join([":---:" if c == "ID" else ":---" for c in COLUMNS_22]) + " |"
        rows = [gene.to_markdown_row() for gene in skills]

        content = (
            "# TABELA GENÉTICA DE SKILLS DO METAPIRA\n\n"
            f"> Capacidade: {len(skills)}/{self.MAX_SKILLS} slots de habilidades cognitivas ativas.\n\n"
            f"{header}\n{sep}\n" + "\n".join(rows) + "\n"
        )

        try:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar tabela de skills em {dest}: {e}")
            return False

    def get_table_markdown(self) -> str:
        if os.path.exists(self.table_path):
            try:
                with open(self.table_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return "Tabela genética não encontrada."

    def deploy_staging(self) -> str:
        if not os.path.exists(self.staging_path):
            return "Nenhum staging pendente para deploy."
        try:
            if os.path.exists(self.table_path):
                shutil.copy(self.table_path, self.backup_path)
            shutil.move(self.staging_path, self.table_path)
            return "🚀 Deploy concluído! Tabela Genética de Skills atualizada."
        except Exception as e:
            return f"[ERRO]: Falha no deploy: {str(e)}"

    def rollback(self) -> str:
        if not os.path.exists(self.backup_path):
            return "Nenhum backup disponível para rollback."
        try:
            shutil.copy(self.backup_path, self.table_path)
            return "⏪ Rollback executado com sucesso! Backup restaurado."
        except Exception as e:
            return f"[ERRO]: Falha no rollback: {str(e)}"

    def evaluate_and_evolve(self, user_msg: str, bot_response: str, llm_client) -> Optional[str]:
        skills = self.load_skills()
        qtd_atual = len(skills)

        prompt_sistema = (
            "Você é o Auditor Genético do Metapira Engine.\n"
            "Sua tarefa é analisar a interação recente entre o usuário e o bot para determinar se houve o surgimento de uma nova habilidade/estratégia relevante ou necessidade de ajuste nos genes existentes.\n\n"
            f"ESTADO ATUAL DA TABELA: {qtd_atual}/{self.MAX_SKILLS} habilidades preenchidas.\n"
            "COLUNAS OBRIGATÓRIAS (22):\n"
            "ID | Layer1_Style | ENTITY | Impact | Layer2_Archetype | Layer3_Domain | Layer4_Valence | Layer5_Strategy | Influence_Weight | Conflict_Status | Activation_Phrase_1 .. Activation_Phrase_12\n\n"
            "REGRAS DE DECISÃO:\n"
            "1. Se a interação for trivial, irrelevante ou não trouxer novo padrão cognitivo/habilidade: responda APENAS: NENHUMA_MUDANCA\n"
            f"2. Se for relevante E houver menos de 10 skills ({qtd_atual} < 10): Crie UMA nova linha para ID {qtd_atual + 1} com todas as 22 colunas preenchidas separadas por '|'.\n"
            "3. Se for relevante E a tabela JÁ TIVER 10 skills (10/10): Selecione o ID (de 1 a 10) mais impactado por essa interação e reescreva sua linha completa atualizando estratégias, pesos ou frases de ativação.\n\n"
            "FORMATO DE RETORNO:\n"
            "Se for mudar, retorne EXCLUSIVAMENTE a linha markdown correspondente no formato:\n"
            "| ID | Layer1_Style | ENTITY | Impact | Layer2_Archetype | Layer3_Domain | Layer4_Valence | Layer5_Strategy | Influence_Weight | Conflict_Status | Frase1 | Frase2 | Frase3 | Frase4 | Frase5 | Frase6 | Frase7 | Frase8 | Frase9 | Frase10 | Frase11 | Frase12 |\n"
            "Não adicione introduções ou conclusões."
        )

        user_content = (
            f"[INTERAÇÃO RECENTE]\nUsuário: {user_msg}\nBot: {bot_response}\n\n"
            f"[TABELA ATUAL]\n{self.get_table_markdown()}"
        )

        try:
            resposta = llm_client.chat(prompt_sistema, user_content, temp=0.5)
            if not resposta or "NENHUMA_MUDANCA" in resposta.upper():
                return None

            for line in resposta.splitlines():
                line = line.strip()
                if line.startswith("|") and ("|" in line[1:]):
                    gene_novo = SkillGene.from_markdown_row(line)
                    if gene_novo:
                        # Se já existe esse ID, atualiza
                        updated = False
                        for i, g in enumerate(skills):
                            if g.id == gene_novo.id:
                                skills[i] = gene_novo
                                updated = True
                                break
                        
                        if not updated:
                            if len(skills) < self.MAX_SKILLS:
                                gene_novo.id = len(skills) + 1
                                skills.append(gene_novo)
                            else:
                                # Se atingiu 10 e id veio fora do escopo, atualiza o ID 10
                                gene_novo.id = 10
                                skills[9] = gene_novo

                        # Backup e salvar
                        if os.path.exists(self.table_path):
                            shutil.copy(self.table_path, self.backup_path)
                        self.save_skills(skills)
                        logging.info(f"🧬 Gene {gene_novo.id} atualizado/adicionado com sucesso.")
                        return f"Gene ID {gene_novo.id} ({gene_novo.layer3_domain}) sintetizado."
        except Exception as e:
            logging.warning(f"Falha ao avaliar evolução de skills: {e}")

        return None

# ==============================================================================
# MÓDULO CONCATENADO: src/llm.py
# ==============================================================================
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

# ==============================================================================
# MÓDULO CONCATENADO: src/pipeline.py
# ==============================================================================
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

# ==============================================================================
# MÓDULO CONCATENADO: src/bot.py
# ==============================================================================
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

try:
    from .config import Config
    from .security import SecuritySentinel
    from .memory import BM25Memory
    from .skills import SkillManager
    from .llm import DeepSeekClient
    from .pipeline import CognitivePipeline
except (ImportError, ValueError):
    # Quando concatenado em main.py pelo install.sh, as classes já estão no escopo global
    pass

class MetapiraTelegramBot:
    def __init__(self, config):
        self.config = config
        self.sentinel = SecuritySentinel(config.arq_seguranca)
        self.memory = BM25Memory(config.arq_historico)
        self.skill_mgr = SkillManager(config.arq_tabela, config.arq_staging, config.arq_backup)
        self.llm = DeepSeekClient(config.deepseek_key, config.deepseek_url)
        self.pipeline = CognitivePipeline(
            config=self.config,
            sentinel=self.sentinel,
            memory=self.memory,
            skill_mgr=self.skill_mgr,
            llm=self.llm
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        skills = self.skill_mgr.load_skills()
        msg = (
            "🤖 *Metapira Cognitive Engine Online*\n\n"
            f"• Skills ativas: `{len(skills)}/10`\n"
            "• Comandos:\n"
            "  `/status` - Diagnóstico de memória e engine\n"
            "  `/genes` - Tabela viva de 22 colunas de skills\n"
            "  `/help` - Resumo operacional\n\n"
            "_Comandos de Administrador:_\n"
            "  `/evolve` - Forçar ciclo evolutivo de habilidades\n"
            "  `/deploy` - Aplicar tabela em staging\n"
            "  `/rollback` - Reverter para o último backup"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.start(update, context)

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        skills = self.skill_mgr.load_skills()
        total_interacoes = self.memory.count_interactions()
        
        status_msg = (
            f"📊 *Diagnóstico do Metapira Engine*\n\n"
            f"• Capacidade de Skills: `{len(skills)}/10` habilidades\n"
            f"• Total de Interações (BM25): `{total_interacoes}`\n"
            f"• Admin Autorizado ID: `{self.config.admin_id}`\n"
            f"• DeepSeek Configurado: `{'Sim' if self.llm.is_configured() else 'Não'}`"
        )
        await update.message.reply_text(status_msg, parse_mode="Markdown")

    async def cmd_genes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tabela = self.skill_mgr.get_table_markdown()
        if len(tabela) > 4000:
            tabela = tabela[:3900] + "\n\n... (truncado para limite do Telegram)"
        await update.message.reply_text(f"🧬 *Tabela Genética de Skills (22 Colunas):*\n\n{tabela}")

    async def cmd_evolve(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.config.admin_id:
            await update.message.reply_text("⛔ Acesso não autorizado. Apenas o Admin pode invocar /evolve.")
            return

        await update.message.reply_text("⏳ Disparando ciclo de auto-análise e evolução de skills...")
        historico = self.memory.get_recent_history_text(3000)
        res = await asyncio.to_thread(
            self.skill_mgr.evaluate_and_evolve,
            "Revisão forçada pelo administrador",
            historico,
            self.llm
        )
        if res:
            await update.message.reply_text(f"✅ Ciclo concluído: {res}")
        else:
            await update.message.reply_text("ℹ️ Nenhuma mutação necessária. A tabela atual permanece ótima.")

    async def cmd_deploy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.config.admin_id:
            await update.message.reply_text("⛔ Acesso não autorizado.")
            return
        res = self.skill_mgr.deploy_staging()
        await update.message.reply_text(res)

    async def cmd_rollback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.config.admin_id:
            await update.message.reply_text("⛔ Acesso não autorizado.")
            return
        res = self.skill_mgr.rollback()
        await update.message.reply_text(res)

    async def handle_msg(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return

        texto = update.message.text.strip()
        chat_type = update.effective_chat.type

        # Tratamento de grupos: responder apenas quando mencionado ou em resposta
        if chat_type != "private":
            bot_username = context.bot.username or ""
            mencionado = False

            if update.message.entities:
                for ent in update.message.entities:
                    if ent.type == "mention":
                        m = texto[ent.offset : ent.offset + ent.length]
                        if bot_username and m.lower() == f"@{bot_username}".lower():
                            mencionado = True
                            break

            if not mencionado and bot_username and f"@{bot_username}".lower() in texto.lower():
                mencionado = True

            if not mencionado and update.message.reply_to_message:
                if update.message.reply_to_message.from_user.id == context.bot.id:
                    mencionado = True

            if not mencionado:
                return

        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        except Exception:
            pass

        resposta = await asyncio.to_thread(self.pipeline.process_message, texto)

        # Envio em blocos para respeitar o limite de 4096 caracteres
        for i in range(0, len(resposta), 4000):
            bloco = resposta[i : i + 4000]
            await update.message.reply_text(bloco)

    def run(self):
        if not self.config.telegram_token:
            logging.error("ERRO: TELEGRAM_TOKEN não configurado. Verifique o .env!")
            return

        logging.info("Iniciando Metapira Telegram Bot...")
        app = ApplicationBuilder().token(self.config.telegram_token).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.cmd_help))
        app.add_handler(CommandHandler("status", self.cmd_status))
        app.add_handler(CommandHandler("genes", self.cmd_genes))
        app.add_handler(CommandHandler("evolve", self.cmd_evolve))
        app.add_handler(CommandHandler("deploy", self.cmd_deploy))
        app.add_handler(CommandHandler("rollback", self.cmd_rollback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_msg))

        logging.info("Bot rodando com sucesso. Aguardando mensagens...")
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

def main():
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    cfg = Config.load()
    bot = MetapiraTelegramBot(cfg)
    bot.run()

if __name__ == "__main__":
    main()
