# GENERATION.md — Système de génération de contenu
> Dernière mise à jour : 2 février 2026

## Vue d'ensemble

Le contenu est généré via l'API Claude (Anthropic) avec des scripts Python/Bash.

## Credentials

```
API Key : stockée dans /home/ubuntu/hbb/.secrets
Format  : ANTHROPIC_API_KEY=sk-ant-api03-...
Perms   : chmod 600 (gitignored)
Modèle  : claude-sonnet-4-20250514
```

## Structure du dossier generation/

```
/home/ubuntu/hbb/generation/
├── run.sh                    # Script wrapper principal
├── generate_content.py       # Génération homepage + auteurs via API
├── integrate_content.py      # Intégration du contenu généré dans Hugo
├── generate_category_seo.py  # Génération SEO catégories
├── gen_seo_langs.py          # Génération SEO multilingue
├── data/                     # JSON générés par parfum (13 fichiers)
├── templates/                # Templates frontmatter
├── translations/             # Traductions notes olfactives
├── scripts/                  # Scripts utilitaires
├── logs/                     # Historique des générations
└── .secrets/                 # (legacy) Copie API key
```

## Commandes run.sh

```bash
cd /home/ubuntu/hbb/generation
./run.sh homepage   # Générer textes SEO homepage
./run.sh authors    # Générer bios auteurs
./run.sh all        # Générer tout
./run.sh integrate  # Intégrer dans Hugo
./run.sh status     # État du projet
./run.sh deploy     # git add + commit + push
```

## Script gen_all.sh (génération SEO catégories 14 langues)

Créé le 1er février 2026 dans `/home/ubuntu/gen_all.sh` :
- Génère le contenu SEO pour les 4 catégories × 14 langues
- Appelle l'API Claude avec des prompts structurés
- Merge les résultats dans data/categories/*.json
- Auto-commit et push

```bash
# Exécution (TOUJOURS en background pour éviter timeout MCP)
nohup bash /home/ubuntu/gen_all.sh > /dev/null 2>&1 &
# Suivi
tail -f /tmp/gen_all.log
```

## Pattern pour appels API Claude

```bash
# ⚠️ TOUJOURS utiliser nohup pour les commandes longues (API calls, scripts)
nohup bash mon_script.sh > /dev/null 2>&1 &

# Suivi via logs
tail -f /tmp/mon_log.log
```

### Exemple d'appel API direct

```bash
API_KEY=$(grep ANTHROPIC_API_KEY /home/ubuntu/hbb/.secrets | cut -d= -f2)

curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "messages": [{"role":"user","content":"..."}]
  }'
```

## Workflow de génération type

1. Créer un script bash qui boucle sur les langues/catégories
2. Pour chaque itération : appeler l'API Claude avec un prompt structuré
3. Parser la réponse JSON
4. Merger dans le fichier data/ ou content/ cible
5. Valider avec `hugo server` (ou vérifier le build)
6. `git add . && git commit -m "..." && git push origin main`

## Données de génération existantes

```
generation/data/         # 13 fichiers JSON (1 par parfum)
generation/translations/ # notes_translations.json, perfume_translations.json
```

Ces fichiers contiennent les données source utilisées pour générer les pages parfums dans les 14 langues.

## Briefs de génération (prompts/)

```
generation/prompts/
├── perfumes.txt     # Brief pour articles parfums EN
├── skincare.txt     # Brief pour articles skincare EN
├── makeup.txt       # Brief pour articles makeup EN
├── haircare.txt     # Brief pour articles haircare EN
└── translate.txt    # Brief pour traduction EN → 13 langues
```

### Brief translate.txt — Points clés
- Réécriture native, PAS traduction littérale
- translationKey : copier EXACTEMENT depuis EN (CRITICAL)
- images : copier EXACTEMENT depuis EN (CRITICAL)
- subcategories : garder en anglais (slugs = noms de dossiers)
- Devises : € pour langues européennes (FR/DE/ES/IT/PT/NL/PL/TR), devises locales pour l'Asie
- Tags/keywords entre guillemets doubles obligatoire : `["valeur 1", "valeur 2"]`
- Minimum 3 H2 + 6 H3

### Script de traduction test

```bash
# Traduit un article EN vers FR/DE/ES/ZH
python3 generation/test_translate_fenty.py
```

## Listes de produits

```
generation/product_lists/
├── perfumes.json    # 511 produits
├── skincare.json    # 278 produits
├── makeup.json      # 500 produits
├── haircare.json    # 270 produits
└── gaps.json        # 70 produits pour combler sous-cat < 3
```

Total : 1 629 produits à générer.

## Workflow de génération de masse (à venir)

1. Renseigner URLs images via interface (4 URLs max par produit)
2. Télécharger images → `static/images/{category}/`
3. Générer fiche EN via API Claude + brief catégorie
4. Traduire EN → 13 langues via API Claude + brief translate.txt
5. Git push → auto-deploy Cloudflare (~2 min)
