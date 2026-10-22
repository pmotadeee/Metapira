#!/bin/bash
# ==============================================================================
# installer/concatenator.sh - Concatenador dos Módulos Python OOP em main.py
# ==============================================================================

concatenate_scripts() {
    echo -e "${C_BLUE}${C_BOLD}[4/6] Lendo diretórios e concatenando módulos Python OOP em main.py...${C_RESET}"
    
    OUTPUT_FILE="main.py"
    
    cat << 'EOF' > "$OUTPUT_FILE"
# ==============================================================================
# METAPIRA COGNITIVE ENGINE - MONÓLITO AUTO-CONCATENADO
# Arquitetura: OOP Modularizada -> Monólito Final via install.sh
# ==============================================================================
EOF

    MODULES=(
        "src/config.py"
        "src/security.py"
        "src/memory.py"
        "src/skills.py"
        "src/llm.py"
        "src/pipeline.py"
        "src/bot.py"
    )

    for mod in "${MODULES[@]}"; do
        if [ -f "$mod" ]; then
            echo -e "  [+] Concatenando módulo: ${C_CYAN}$mod${C_RESET}"
            echo -e "\n# ==============================================================================" >> "$OUTPUT_FILE"
            echo -e "# MÓDULO CONCATENADO: $mod" >> "$OUTPUT_FILE"
            echo -e "# ==============================================================================" >> "$OUTPUT_FILE"
            cat "$mod" >> "$OUTPUT_FILE"
        else
            echo -e "  ${C_RED}✗ Aviso: $mod não encontrado!${C_RESET}"
        fi
    done

    echo -e "  ${C_GREEN}✓ Script final $OUTPUT_FILE montado com sucesso ($(wc -l < "$OUTPUT_FILE") linhas).${C_RESET}\n"
}
