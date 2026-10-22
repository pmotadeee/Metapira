#!/bin/bash
# ==============================================================================
# installer/env_check.sh - Detecção e Validação do Ambiente do Sistema
# ==============================================================================

check_environment() {
    echo -e "${C_BLUE}${C_BOLD}[1/6] Verificando ambiente e pré-requisitos...${C_RESET}"
    
    IS_TERMUX=false
    if [ -d "/data/data/com.termux" ] || [ -n "$TERMUX_VERSION" ]; then
        IS_TERMUX=true
        echo -e "  ${C_GREEN}✓ Ambiente detectado: Termux (Android)${C_RESET}"
    else
        echo -e "  ${C_GREEN}✓ Ambiente detectado: Linux Standard / Server${C_RESET}"
    fi

    if ! command -v python3 &>/dev/null; then
        echo -e "${C_RED}✗ Python 3 não foi encontrado!${C_RESET}"
        if [ "$IS_TERMUX" = true ]; then
            echo -e "${C_YELLOW}Instalando Python via pkg...${C_RESET}"
            pkg update -y && pkg install python -y
        else
            echo -e "${C_RED}Por favor instale o Python 3 antes de continuar:${C_RESET}"
            echo "  Debian/Ubuntu: sudo apt update && sudo apt install python3 python3-venv python3-pip -y"
            exit 1
        fi
    else
        PY_VER=$(python3 --version 2>&1)
        echo -e "  ${C_GREEN}✓ $PY_VER verificado.${C_RESET}"
    fi

    echo ""
}
