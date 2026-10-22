#!/bin/bash
# ==============================================================================
# installer/finalize.sh - Scripts de Inicialização e Inicialização Opcional
# ==============================================================================

finalize_installation() {
    echo -e "${C_BLUE}${C_BOLD}[6/6] Finalizando instalação e gerando scripts de execução...${C_RESET}"

    # run.sh
    cat << 'EOF' > run.sh
#!/bin/bash
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

if [ -f "venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
fi

exec python3 main.py
EOF
    chmod +x run.sh

    # metapira.service (para Linux)
    cat << EOF > metapira.service
[Unit]
Description=Metapira Cognitive Engine
After=network.target

[Service]
Type=simple
User=${USER:-root}
WorkingDirectory=${BASE_DIR}
EnvironmentFile=${BASE_DIR}/.env
ExecStart=${BASE_DIR}/venv/bin/python ${BASE_DIR}/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    echo -e "  ${C_GREEN}✓ Script run.sh e serviço metapira.service gerados.${C_RESET}\n"

    echo -e "${C_GREEN}${C_BOLD}================================================================================${C_RESET}"
    echo -e "${C_GREEN}${C_BOLD}                 INSTALAÇÃO CONCLUÍDA COM SUCESSO! 🚀                           ${C_RESET}"
    echo -e "${C_GREEN}${C_BOLD}================================================================================${C_RESET}"
    echo -e "Módulos OOP concatenados com sucesso em ${C_CYAN}main.py${C_RESET}."
    echo -e "Tabela de skills inicializada com ${C_CYAN}22 colunas${C_RESET} (IDs dinâmicos de 1 a 10)."
    echo ""
    echo -e "Comandos de execução:"
    echo -e "  • Rodar em primeiro plano:         ${C_CYAN}./run.sh${C_RESET}"
    echo -e "  • Rodar em segundo plano (Termux): ${C_CYAN}nohup ./run.sh > metapira.log 2>&1 &${C_RESET}"
    echo -e "  • Acompanhar logs:                 ${C_CYAN}tail -f metapira.log${C_RESET}"
    echo ""

    read -r -p "Deseja iniciar o Metapira agora? [S/n]: " RESPOSTA
    RESPOSTA="${RESPOSTA:-S}"

    if [[ "$RESPOSTA" =~ ^[Ss]$ ]]; then
        echo -e "\n${C_GREEN}Iniciando o bot... (Pressione Ctrl+C para parar)${C_RESET}\n"
        exec ./run.sh
    else
        echo -e "\n${C_CYAN}Tudo pronto! Para iniciar quando quiser, execute: ./run.sh${C_RESET}\n"
    fi
}
