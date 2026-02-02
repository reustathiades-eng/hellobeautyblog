# ARCHITECTURE.md — HelloBeautyBlog
> Dernière mise à jour : 2 février 2026

## Vue d'ensemble

Site beauté multilingue (14 langues), Hugo + Cloudflare Pages + GitHub.
- Production : https://hellobeautyblog.com
- Serveur dev : olfapedia:exec → /home/ubuntu/hbb

## Arborescence racine

```
/home/ubuntu/hbb/
├── config/_default/
│   ├── config.yaml         # Config Hugo (baseURL, theme, taxonomies)
│   ├── languages.yaml      # 14 langues (slugs, permalinks, menus)
│   └── params.yaml         # Design, couleurs, typo, SEO, affiliation
├── content/                # Contenu par langue (voir LANGUAGES.md)
├── data/                   # JSON pour SEO et catégories (voir DATA_STRUCTURE.md)
├── static/images/          # Images organisées par type
├── themes/hellobeauty/     # Thème custom (voir TEMPLATES.md)
├── generation/             # Scripts génération API Claude (voir GENERATION.md)
├── docs/                   # Cette documentation
├── .secrets                # ANTHROPIC_API_KEY (chmod 600, gitignored)
└── .gitignore              # Exclut .secrets, generation/.secrets/, public/, logs
```

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| CMS | Hugo 0.121.0 (Static Site Generator) |
| Hébergement | Cloudflare Pages (build auto sur push) |
| Versioning | GitHub (reustathiades-eng/hellobeautyblog) |
| Thème | hellobeauty (custom, dans themes/) |
| Génération contenu | API Claude (claude-sonnet-4-20250514) |
| Fonts | Playfair Display (headings) + Inter (body) |
| Design | Fresh & Modern, rose poudré (#F8C8DC) |

## Config Hugo critique

```yaml
# config/_default/config.yaml
theme: "hellobeauty"                    # ⚠️ OBLIGATOIRE sinon redirect loop
defaultContentLanguage: "en"
defaultContentLanguageInSubdir: true     # ⚠️ OBLIGATOIRE → /en/, /fr/ etc.
disableKinds: [taxonomy, term]           # Taxonomies désactivées au niveau kind
```

## Build Cloudflare

```
Build command: hugo --minify
Output directory: public
Variable: HUGO_VERSION = 0.121.0
Trigger: push sur main → build auto ~2 min
```

## Workflow déploiement

```bash
cd /home/ubuntu/hbb
# Modifier fichiers...
git add . && git commit -m "description" && git push origin main
# Cloudflare détecte le push et rebuild automatiquement
```
