#!/bin/bash
# ==============================================================================
# Wrapper para compatibilidade com ./setup.sh
# Redireciona diretamente para o auto-instalador guiado install.sh
# ==============================================================================
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$BASE_DIR/install.sh" "$@"
