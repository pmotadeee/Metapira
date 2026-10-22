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
