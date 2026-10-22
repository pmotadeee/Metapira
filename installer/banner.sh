#!/bin/bash
# ==============================================================================
# installer/banner.sh - Apresentação Visual e Boas-Vindas
# ==============================================================================

show_banner() {
    clear 2>/dev/null || true
    cat << "EOF"
================================================================================
   __  __ _____ _____  _    ____ ___ ____      _    
  |  \/  | ____|_   _|/ \  |  _ \_ _|  _ \    / \   
  | |\/| |  _|   | | / _ \ | |_) | || |_) |  / _ \  
  | |  | | |___  | |/ ___ \|  __/| ||  _ <  / ___ \ 
  |_|  |_|_____| |_/_/   \_\_|  |___|_| \_\/_/   \_\
      COGNITIVE ENGINE — INSTALADOR MODULAR EM BASH
================================================================================
EOF
    echo -e "${C_CYAN}${C_BOLD}Bem-vindo ao instalador modular do Metapira Engine!${C_RESET}"
    echo -e "Arquitetura OOP com sistema de auto-concatenação de módulos e matriz genética de 22 colunas.\n"
}
