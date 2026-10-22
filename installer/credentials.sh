#!/bin/bash
# ==============================================================================
# installer/credentials.sh - Coleta Guiada de Credenciais e Direcionamentos
# ==============================================================================

collect_credentials() {
    echo -e "${C_BLUE}${C_BOLD}[2/6] Configuração Guiada de Credenciais...${C_RESET}"
    echo -e "O Metapira precisa de 3 credenciais para conectar ao Telegram e DeepSeek.\n"

    # Carregar existentes se houver
    if [ -f .env ]; then
        # shellcheck disable=SC1091
        source .env 2>/dev/null || true
    fi

    # 1. TELEGRAM_TOKEN
    echo -e "${C_YELLOW}${C_BOLD}--- DIREÇÃO 1: TOKEN DO TELEGRAM ---${C_RESET}"
    echo -e "Necessário para a comunicação do bot no Telegram."
    echo -e "${C_CYAN}Como obter:${C_RESET}"
    echo -e "  1. Acesse o ${C_BOLD}@BotFather${C_RESET} no Telegram."
    echo -e "  2. Digite ${C_BOLD}/newbot${C_RESET} e configure o nome e @username do bot."
    echo -e "  3. Copie o token HTTP API gerado (ex: 8718691851:AAGRQZo...)"
    echo ""
    read -r -p "Informe seu TELEGRAM_TOKEN [${TELEGRAM_TOKEN:-obrigatorio}]: " INPUT_TG
    TELEGRAM_TOKEN="${INPUT_TG:-$TELEGRAM_TOKEN}"
    while [ -z "$TELEGRAM_TOKEN" ]; do
        echo -e "${C_RED}TELEGRAM_TOKEN não pode ser vazio.${C_RESET}"
        read -r -p "Informe seu TELEGRAM_TOKEN: " TELEGRAM_TOKEN
    done
    echo -e "  ${C_GREEN}✓ Telegram Token registrado.${C_RESET}\n"

    # 2. DEEPSEEK_KEY
    echo -e "${C_YELLOW}${C_BOLD}--- DIREÇÃO 2: CHAVE DE API DA DEEPSEEK ---${C_RESET}"
    echo -e "Cérebro cognitivo responsável pelo raciocínio e síntese das 22 colunas de skills."
    echo -e "${C_CYAN}Como obter:${C_RESET}"
    echo -e "  1. Acesse: ${C_BOLD}https://platform.deepseek.com/api_keys${C_RESET}"
    echo -e "  2. Crie uma nova API Key e copie o valor gerado (inicia com 'sk-...')"
    echo ""
    read -r -p "Informe sua DEEPSEEK_KEY [${DEEPSEEK_KEY:-obrigatorio}]: " INPUT_DS
    DEEPSEEK_KEY="${INPUT_DS:-$DEEPSEEK_KEY}"
    while [ -z "$DEEPSEEK_KEY" ]; do
        echo -e "${C_RED}DEEPSEEK_KEY não pode ser vazia.${C_RESET}"
        read -r -p "Informe sua DEEPSEEK_KEY: " DEEPSEEK_KEY
    done
    echo -e "  ${C_GREEN}✓ DeepSeek Key registrada.${C_RESET}\n"

    # 3. ADMIN_ID
    echo -e "${C_YELLOW}${C_BOLD}--- DIREÇÃO 3: SEU ID NUMÉRICO (ADMIN_ID) ---${C_RESET}"
    echo -e "Autoridade máxima para comandos de mutação (/evolve), implantação (/deploy) e rollback."
    echo -e "${C_CYAN}Como obter:${C_RESET}"
    echo -e "  1. No Telegram, envie uma mensagem para o bot ${C_BOLD}@userinfobot${C_RESET}."
    echo -e "  2. Copie o número exibido em ${C_BOLD}Id:${C_RESET} (exemplo: 987654321)"
    echo ""
    read -r -p "Informe seu ADMIN_ID [${ADMIN_ID:-0}]: " INPUT_ADM
    ADMIN_ID="${INPUT_ADM:-$ADMIN_ID}"
    while [ -z "$ADMIN_ID" ] || [ "$ADMIN_ID" = "0" ]; do
        echo -e "${C_RED}Informe seu ID numérico do Telegram.${C_RESET}"
        read -r -p "Informe seu ADMIN_ID: " ADMIN_ID
    done
    echo -e "  ${C_GREEN}✓ Admin ID registrado: $ADMIN_ID${C_RESET}\n"

    # Gravar arquivo .env
    cat << EOF > .env
TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
DEEPSEEK_KEY=${DEEPSEEK_KEY}
ADMIN_ID=${ADMIN_ID}
EOF
    chmod 600 .env
    echo -e "  ${C_GREEN}✓ Arquivo .env salvo com segurança (permissão 600).${C_RESET}\n"
}
