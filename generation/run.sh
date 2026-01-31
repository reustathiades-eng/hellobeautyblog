#!/bin/bash
#######################################################
# HelloBeautyBlog - Script wrapper de génération
# Usage: ./run.sh [command]
#######################################################

cd /home/ubuntu/hbb/generation

# Charger l'API key
if [ -f ".secrets/api_keys" ]; then
    export $(cat .secrets/api_keys | xargs)
elif [ -f "../.secrets" ]; then
    export $(grep ANTHROPIC_API_KEY ../.secrets | xargs)
fi

# Vérifier que l'API key est chargée
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERREUR: ANTHROPIC_API_KEY non trouvée"
    exit 1
fi

echo "✅ API Key chargée: ${ANTHROPIC_API_KEY:0:20}..."

case "$1" in
    "homepage")
        echo "🏠 Génération du contenu homepage..."
        python generate_content.py homepage
        ;;
    "authors")
        echo "👤 Génération des bios auteurs..."
        python generate_content.py authors
        ;;
    "all")
        echo "🚀 Génération de tout le contenu..."
        python generate_content.py all
        ;;
    "integrate")
        echo "📥 Intégration dans Hugo..."
        python integrate_content.py all
        ;;
    "status")
        echo ""
        echo "📊 ÉTAT DU PROJET HELLOBEAUTYBLOG"
        echo "=================================="
        echo ""
        echo "📁 Contenu généré:"
        ls -la *.json 2>/dev/null || echo "  Aucun fichier JSON"
        echo ""
        echo "📝 Derniers logs:"
        ls -lt logs/*.log 2>/dev/null | head -5
        echo ""
        echo "🌐 Langues configurées: 14"
        echo "👤 Auteurs configurés: 4"
        ;;
    "deploy")
        echo "🚀 Commit et déploiement..."
        cd /home/ubuntu/hbb
        git add .
        git commit -m "Update: Generated content $(date +%Y-%m-%d)"
        git push origin main
        echo "✅ Déployé ! Cloudflare build en cours (~2 min)"
        ;;
    *)
        echo "Usage: $0 {homepage|authors|all|integrate|status|deploy}"
        echo ""
        echo "Commands:"
        echo "  homepage  - Générer les textes homepage SEO"
        echo "  authors   - Générer les bios des auteurs"
        echo "  all       - Générer tout le contenu"
        echo "  integrate - Intégrer le contenu dans Hugo"
        echo "  status    - Voir l'état du projet"
        echo "  deploy    - Commit et push vers GitHub"
        ;;
esac
