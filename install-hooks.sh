#!/bin/bash
# =============================================================
# install-hooks.sh — Installation des hooks Git
# =============================================================
# Usage : bash install-hooks.sh
# =============================================================

echo "Installation des hooks Git..."

# Méthode 1 : configurer le chemin des hooks (recommandée)
git config core.hooksPath .git-hooks

# Rendre les hooks exécutables
chmod +x .git-hooks/pre-commit
chmod +x .git-hooks/commit-msg
chmod +x .git-hooks/pre-push

echo "✓ Hooks installés via core.hooksPath"
echo ""
echo "Hooks actifs :"
echo "  pre-commit  → vérification syntaxe Python, secrets, .env"
echo "  commit-msg  → format Conventional Commits"
echo "  pre-push    → interdit push direct sur main"
echo ""
echo "Pour tester :"
echo "  git commit -m 'message invalide'   → doit échouer"
echo "  git commit -m 'feat: message OK'   → doit passer"
