# 🧬 Metapira Cognitive Engine

Monólito cognitivo autônomo para Telegram integrado com a API DeepSeek, memória dinâmica vetorial/BM25 e sistema de auto-evolução genética.

---

## ⚡ Como Instalar

Para instalar ou configurar o bot (seja no Termux/Android ou em qualquer servidor Linux):

```bash
chmod +x install.sh
./install.sh
```

*(Ou utilize `./setup.sh`)*

### O Instalador Guiado Cuida de Tudo:
1. **Orientações Interativas:** Explica passo a passo como obter o `TELEGRAM_TOKEN` no @BotFather, a `DEEPSEEK_KEY` na plataforma DeepSeek e o seu `ADMIN_ID` no @userinfobot.
2. **Arquitetura Cognitiva:** Gera automaticamente todos os prompts com comentários e direcionamentos:
   - `config/prompts/seguranca.md` (Sentinela de proteção)
   - `config/prompts/roteador.md` (Roteador de resposta e persona)
   - `config/prompts/evolucao.md` (Motor de auto-mutação da tabela)
   - `config/genes/tabela_genetica.md` (Tabela viva)
3. **Ambiente Python:** Cria o `venv` apropriado e instala as dependências (`python-telegram-bot`, `requests`, `rank-bm25`).
4. **Execução:** Pergunta se deseja iniciar o bot imediatamente ou dá as instruções de background.

---

## 🚀 Como Iniciar

### Em Primeiro Plano:
```bash
./run.sh
```

### Em Segundo Plano no Termux (Mantém rodando):
```bash
nohup ./run.sh > metapira.log 2>&1 &
```
Acompanhe os logs em tempo real:
```bash
tail -f metapira.log
```

---

## 🛠️ Comandos no Telegram

### Para Usuários:
- `/start` - Inicialização e menu de boas-vindas.
- `/status` - Diagnóstico de saúde e linhas na memória BM25.
- `/genes` - Exibe a tabela genética viva em Markdown.
- `/help` - Resumo de comandos e funcionamento.

### Exclusivos do Administrador (`ADMIN_ID`):
- `/evolve` - Aciona a DeepSeek para sintetizar uma nova tabela genética baseada nas últimas conversas (`staging_tabela.md`).
- `/deploy` - Promove a versão de staging para a tabela viva, gerando backup automático da anterior.
- `/rollback` - Restaura imediatamente o backup anterior da tabela genética.
