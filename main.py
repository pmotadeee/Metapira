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
class Usuario:
    """
    Classe Usuario:
    Representa a entidade de um usuário interagindo com o bot.
    Atualmente deixada vazia (placeholder) conforme especificação de design
    para futura expansão de estado, preferências e histórico por usuário.
    """
    def __init__(self, id_usuario: int = None, username: str = None, nome: str = None):
        self.id_usuario = id_usuario
        self.username = username
        self.nome = nome
        # Espaço reservado: deixado vazio para implementações futuras
        pass
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
import os
import json
import logging
from datetime import datetime
from rank_bm25 import BM25Okapi

class MemoriaBM25:
    """
    Classe MemoriaBM25:
    Armazena o histórico em JSON Lines e realiza busca de contexto
    relevante com tokenização e ranking Okapi BM25.
    """
    def __init__(self, caminho_historico: str):
        self.caminho_historico = caminho_historico
        os.makedirs(os.path.dirname(self.caminho_historico), exist_ok=True)

    def buscar_contexto(self, query: str, top_n: int = 4) -> str:
        if not os.path.exists(self.caminho_historico):
            return "Sem histórico prévio disponível."

        docs = []
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            d = json.loads(line)
                            docs.append(f"Usuário: {d.get('user', '')}\nBot: {d.get('bot', '')}")
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logging.warning(f"Erro ao ler histórico: {e}")
            return "Sem histórico disponível."

        if not docs:
            return "Sem histórico prévio."

        corpus = [doc.lower().split() for doc in docs]
        bm25 = BM25Okapi(corpus)
        top = bm25.get_top_n(query.lower().split(), docs, n=min(top_n, len(docs)))
        return "\n---\n".join(top)

    def salvar(self, user_msg: str, bot_msg: str):
        try:
            with open(self.caminho_historico, "a", encoding="utf-8") as f:
                registro = {
                    "timestamp": datetime.now().isoformat(),
                    "user": user_msg,
                    "bot": bot_msg
                }
                f.write(json.dumps(registro, ensure_ascii=False) + "\n")
        except Exception as e:
            logging.error(f"Erro ao salvar histórico: {e}")

    def contar_registros(self) -> int:
        if not os.path.exists(self.caminho_historico):
            return 0
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0
import os
import re
import shutil
import logging
from dataclasses import dataclass, field
from typing import List, Optional

COLUNAS_SKILLS = [
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

    def to_markdown(self) -> str:
        frases = self.activation_phrases + [""] * (12 - len(self.activation_phrases))
        frases = frases[:12]
        colunas = [
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
        ] + [f.strip() for f in frases]
        return "| " + " | ".join(colunas) + " |"

    @classmethod
    def from_markdown(cls, linha: str) -> Optional["SkillGene"]:
        partes = [p.strip() for p in linha.strip().strip("|").split("|")]
        if len(partes) < 10:
            return None
        try:
            gene_id = int(re.sub(r"[^\d]", "", partes[0]))
        except ValueError:
            return None

        frases = partes[10:22]
        while len(frases) < 12:
            frases.append("")

        return cls(
            id=gene_id,
            layer1_style=partes[1] if len(partes) > 1 else "Direto",
            entity=partes[2] if len(partes) > 2 else "Metapira",
            impact=partes[3] if len(partes) > 3 else "Base",
            layer2_archetype=partes[4] if len(partes) > 4 else "Executor",
            layer3_domain=partes[5] if len(partes) > 5 else "Geral",
            layer4_valence=partes[6] if len(partes) > 6 else "Neutra",
            layer5_strategy=partes[7] if len(partes) > 7 else "Heurística",
            influence_weight=partes[8] if len(partes) > 8 else "0.5",
            conflict_status=partes[9] if len(partes) > 9 else "Alinhado",
            activation_phrases=frases[:12]
        )

class TabelaSkills:
    """
    Classe TabelaSkills:
    Controla os 10 IDs da matriz de habilidades de 22 colunas.
    Soma novas habilidades até 10 IDs e, ao atingir 10,
    atualiza o ID mais relevante com base em cada interação.
    """
    MAX_SKILLS = 10

    def __init__(self, caminho_tabela: str, caminho_staging: str = "", caminho_backup: str = ""):
        self.caminho_tabela = caminho_tabela
        self.caminho_staging = caminho_staging or caminho_tabela.replace(".md", "_staging.md")
        self.caminho_backup = caminho_backup or caminho_tabela.replace(".md", "_backup.md")
        os.makedirs(os.path.dirname(self.caminho_tabela), exist_ok=True)

    def carregar(self) -> List[SkillGene]:
        skills = []
        if not os.path.exists(self.caminho_tabela):
            return skills
        try:
            with open(self.caminho_tabela, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("|") and not ("---" in line) and not ("Layer1_Style" in line):
                        gene = SkillGene.from_markdown(line)
                        if gene:
                            skills.append(gene)
        except Exception as e:
            logging.error(f"Erro ao carregar skills: {e}")
        skills.sort(key=lambda s: s.id)
        return skills[:self.MAX_SKILLS]

    def salvar(self, skills: List[SkillGene], destino: str = None) -> bool:
        dest = destino or self.caminho_tabela
        skills.sort(key=lambda s: s.id)
        skills = skills[:self.MAX_SKILLS]

        header = "| " + " | ".join(COLUNAS_SKILLS) + " |"
        sep = "| " + " | ".join([":---:" if c == "ID" else ":---" for c in COLUNAS_SKILLS]) + " |"
        linhas = [g.to_markdown() for g in skills]

        conteudo = (
            "# TABELA GENÉTICA DE SKILLS DO METAPIRA\n\n"
            f"> Capacidade: {len(skills)}/{self.MAX_SKILLS} slots de habilidades cognitivas.\n\n"
            f"{header}\n{sep}\n" + "\n".join(linhas) + "\n"
        )
        try:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(conteudo)
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar tabela: {e}")
            return False

    def obter_markdown(self) -> str:
        if os.path.exists(self.caminho_tabela):
            try:
                with open(self.caminho_tabela, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return "Tabela de skills não encontrada."

    def deploy(self) -> str:
        if not os.path.exists(self.caminho_staging):
            return "Nenhum staging pendente."
        try:
            if os.path.exists(self.caminho_tabela):
                shutil.copy(self.caminho_tabela, self.caminho_backup)
            shutil.move(self.caminho_staging, self.caminho_tabela)
            return "Deploy concluído. Tabela de skills atualizada."
        except Exception as e:
            return f"[ERRO]: {str(e)}"

    def rollback(self) -> str:
        if not os.path.exists(self.caminho_backup):
            return "Nenhum backup disponível."
        try:
            shutil.copy(self.caminho_backup, self.caminho_tabela)
            return "Rollback executado. Tabela restaurada."
        except Exception as e:
            return f"[ERRO]: {str(e)}"

    def avaliar_e_evoluir(self, user_msg: str, bot_msg: str, api_deepseek) -> Optional[str]:
        skills = self.carregar()
        qtd = len(skills)

        prompt_sistema = (
            "Você é o Auditor Genético do Metapira.\n"
            "Analise a interação entre usuário e bot para avaliar se surgiu nova habilidade relevante ou necessidade de ajuste nos genes existentes.\n"
            f"ESTADO: {qtd}/{self.MAX_SKILLS} skills preenchidas.\n"
            "COLUNAS (22): ID | Layer1_Style | ENTITY | Impact | Layer2_Archetype | Layer3_Domain | Layer4_Valence | Layer5_Strategy | Influence_Weight | Conflict_Status | Frase1 .. Frase12\n\n"
            "REGRAS:\n"
            "1. Se a interação não for relevante para habilidades cognitivas: responda unicamente: NENHUMA_MUDANCA\n"
            f"2. Se for relevante e houver menos de 10 skills ({qtd} < 10): Crie UMA nova linha para ID {qtd + 1} com as 22 colunas separadas por '|'.\n"
            "3. Se já houver 10 skills (10/10): Selecione o ID (1 a 10) mais impactado e retorne a linha completa atualizada com as 22 colunas.\n"
            "Retorne EXCLUSIVAMENTE a linha markdown com as 22 colunas."
        )

        user_content = f"Interação:\nUsuário: {user_msg}\nBot: {bot_msg}\n\nTabela Atual:\n{self.obter_markdown()}"
        try:
            res = api_deepseek.chamar(prompt_sistema, user_content, temp=0.5)
            if not res or "NENHUMA_MUDANCA" in res.upper():
                return None

            for linha in res.splitlines():
                linha = linha.strip()
                if linha.startswith("|") and ("|" in linha[1:]):
                    gene_novo = SkillGene.from_markdown(linha)
                    if gene_novo:
                        atualizado = False
                        for i, g in enumerate(skills):
                            if g.id == gene_novo.id:
                                skills[i] = gene_novo
                                atualizado = True
                                break
                        if not atualizado:
                            if len(skills) < self.MAX_SKILLS:
                                gene_novo.id = len(skills) + 1
                                skills.append(gene_novo)
                            else:
                                gene_novo.id = 10
                                skills[9] = gene_novo

                        if os.path.exists(self.caminho_tabela):
                            shutil.copy(self.caminho_tabela, self.caminho_backup)
                        self.salvar(skills)
                        return f"Gene ID {gene_novo.id} atualizado/sintetizado com sucesso."
        except Exception as e:
            logging.warning(f"Erro na auto-evolução de skills: {e}")
        return None
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
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

class Bot:
    """
    Classe Central Bot:
    Orquestra a inicialização dos Dois Bots (Sentinela e Roteador),
    a API DeepSeek, a Memória BM25 e a Matriz de Skills, gerenciando
    as interações com instâncias da classe Usuario no Telegram.
    """
    def __init__(self, config: Config):
        self.config = config
        self.api = DeepSeekAPI(key=config.deepseek_key, url=config.deepseek_url)
        self.memoria = MemoriaBM25(caminho_historico=config.arq_historico)
        self.skills = TabelaSkills(
            caminho_tabela=config.arq_tabela,
            caminho_staging=config.arq_staging,
            caminho_backup=config.arq_backup
        )
        # Inicialização dos Dois Bots
        self.sentinela = SentinelaBot(caminho_prompt=config.arq_seguranca, api_deepseek=self.api)
        self.roteador = RoteadorBot(
            caminho_prompt=config.arq_roteador,
            api_deepseek=self.api,
            tabela_skills=self.skills,
            memoria=self.memoria
        )

    def processar_interacao(self, usuario: Usuario, mensagem: str) -> str:
        # 1. Avaliação pelo Bot 1 (Sentinela)
        seguro, motivo = self.sentinela.filtrar(mensagem)
        if not seguro:
            return motivo

        # 2. Resposta formulada pelo Bot 2 (Roteador Cognitivo)
        return self.roteador.processar(usuario, mensagem)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        skills_ativas = self.skills.carregar()
        msg = (
            "🤖 *Metapira Engine Online*\n\n"
            f"• Skills ativas na matriz: `{len(skills_ativas)}/10`\n"
            "• Comandos:\n"
            "  `/status` - Diagnóstico dos dois bots e memória BM25\n"
            "  `/genes` - Tabela de skills de 22 colunas\n"
            "  `/help` - Resumo operacional\n\n"
            "_Comandos Admin:_\n"
            "  `/evolve` - Forçar ciclo evolutivo de skills\n"
            "  `/deploy` - Aplicar tabela em staging\n"
            "  `/rollback` - Restaurar backup anterior"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.start(update, context)

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        skills = self.skills.carregar()
        interacoes = self.memoria.contar_registros()
        msg = (
            f"📊 *Diagnóstico do Metapira*\n\n"
            f"• Dois Bots Operacionais: `Sentinela` e `Roteador`\n"
            f"• Matriz de Skills: `{len(skills)}/10` habilidades\n"
            f"• Interações BM25: `{interacoes}`\n"
            f"• Admin ID: `{self.config.admin_id}`\n"
            f"• API DeepSeek: `{'Configurada' if self.api.is_pronta() else 'Pendente'}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def cmd_genes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tabela = self.skills.obter_markdown()
        if len(tabela) > 4000:
            tabela = tabela[:3900] + "\n\n... (truncado para limite do Telegram)"
        await update.message.reply_text(f"🧬 *Matriz Genética de Skills (22 Colunas):*\n\n{tabela}")

    async def cmd_evolve(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.config.admin_id:
            await update.message.reply_text("⛔ Acesso não autorizado.")
            return

        await update.message.reply_text("⏳ Disparando ciclo de auto-análise e mutação de skills...")
        res = await asyncio.to_thread(
            self.skills.avaliar_e_evoluir,
            "Revisão forçada pelo administrador",
            "Atualização de matriz",
            self.api
        )
        if res:
            await update.message.reply_text(f"✅ {res}")
        else:
            await update.message.reply_text("ℹ️ Nenhuma alteração necessária na matriz.")

    async def cmd_deploy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.config.admin_id:
            await update.message.reply_text("⛔ Acesso não autorizado.")
            return
        res = self.skills.deploy()
        await update.message.reply_text(res)

    async def cmd_rollback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.config.admin_id:
            await update.message.reply_text("⛔ Acesso não autorizado.")
            return
        res = self.skills.rollback()
        await update.message.reply_text(res)

    async def handle_msg(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return

        texto = update.message.text.strip()
        chat_type = update.effective_chat.type

        # Tratamento de grupos: responder apenas quando mencionado ou respondido
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

        # Instanciação da classe Usuario
        u = update.effective_user
        usuario = Usuario(id_usuario=u.id, username=u.username, nome=u.first_name)

        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        except Exception:
            pass

        resposta = await asyncio.to_thread(self.processar_interacao, usuario, texto)

        for i in range(0, len(resposta), 4000):
            bloco = resposta[i : i + 4000]
            await update.message.reply_text(bloco)

    def run(self):
        if not self.config.telegram_token:
            logging.error("ERRO CRÍTICO: TELEGRAM_TOKEN não configurado no .env!")
            return

        logging.info("Iniciando Bot Metapira...")
        app = ApplicationBuilder().token(self.config.telegram_token).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.cmd_help))
        app.add_handler(CommandHandler("status", self.cmd_status))
        app.add_handler(CommandHandler("genes", self.cmd_genes))
        app.add_handler(CommandHandler("evolve", self.cmd_evolve))
        app.add_handler(CommandHandler("deploy", self.cmd_deploy))
        app.add_handler(CommandHandler("rollback", self.cmd_rollback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_msg))

        logging.info("Bot rodando em produção. Aguardando mensagens...")
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

def main():
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    cfg = Config()
    bot = Bot(cfg)
    bot.run()

if __name__ == "__main__":
    main()
