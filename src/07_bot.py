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
