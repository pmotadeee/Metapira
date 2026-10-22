#!/bin/bash
# ==============================================================================
# installer/venv.sh - Ambiente Virtual e Instalação de Dependências
# ==============================================================================

setup_virtualenv() {
    echo -e "${C_BLUE}${C_BOLD}[5/6] Configurando ambiente virtual Python e dependências...${C_RESET}"

    # requirements.txt
    cat << 'EOF' > requirements.txt
python-telegram-bot>=20.7
requests>=2.28.0
rank-bm25>=0.2.2
EOF

    VENV_OPTS=""
    if [ "$IS_TERMUX" = true ]; then
        VENV_OPTS="--system-site-packages"
    fi

    if [ ! -d "venv" ]; then
        echo -e "  Criando venv (${VENV_OPTS:-padrão})..."
        python3 -m venv $VENV_OPTS venv
    fi

    # Ativar e instalar
    # shellcheck disable=SC1091
    source venv/bin/activate
    
    echo -e "  Instalando dependências de requirements.txt..."
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet

    echo -e "  ${C_GREEN}✓ Dependências prontas no venv.${C_RESET}\n"
}
