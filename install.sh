#!/bin/bash
# ==============================================================================
#                  METAPIRA COGNITIVE ENGINE - AUTO-INSTALADOR
# ==============================================================================
# Este instalador em Bash:
# 1. Lê os diretórios do projeto e módulos Python em OOP (src/).
# 2. Concatena os módulos OOP no script executável unificado main.py.
# 3. Configura a matriz genética viva de 22 colunas de skills (IDs de 1 a 10).
# 4. Configura credenciais guiadas, virtualenv e dependências.
# ==============================================================================

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

# Carregar módulos do instalador
# shellcheck disable=SC1091
source "$BASE_DIR/installer/colors.sh"
# shellcheck disable=SC1091
source "$BASE_DIR/installer/banner.sh"
# shellcheck disable=SC1091
source "$BASE_DIR/installer/env_check.sh"
# shellcheck disable=SC1091
source "$BASE_DIR/installer/credentials.sh"
# shellcheck disable=SC1091
source "$BASE_DIR/installer/prompts.sh"
# shellcheck disable=SC1091
source "$BASE_DIR/installer/concatenator.sh"
# shellcheck disable=SC1091
source "$BASE_DIR/installer/venv.sh"
# shellcheck disable=SC1091
source "$BASE_DIR/installer/finalize.sh"

# Execução do Fluxo de Instalação
main() {
    show_banner
    check_environment
    collect_credentials
    setup_prompts_and_genes
    concatenate_scripts
    setup_virtualenv
    finalize_installation
}

main "$@"
