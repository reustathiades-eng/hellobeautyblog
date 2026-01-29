# 🌸 Hello Beauty Blog

**Site beauté multilingue automatisé** - Parfums, Soins, Maquillage, Cheveux

[![Deploy to Cloudflare Pages](https://img.shields.io/badge/Deployed%20on-Cloudflare%20Pages-orange)](https://www.hellobeautyblog.com)
[![Hugo](https://img.shields.io/badge/Hugo-0.121+-ff4088)](https://gohugo.io/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🚀 Quick Start

### Prérequis

- [Hugo Extended](https://gohugo.io/installation/) v0.121+
- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) (pour Pagefind search)

### Installation

```bash
# Cloner le repository
git clone https://github.com/votre-username/hellobeautyblog.git
cd hellobeautyblog

# Lancer le serveur de développement
hugo server -D

# Le site est accessible sur http://localhost:1313
```

### Build Production

```bash
# Build du site
hugo --minify

# Build de l'index de recherche
npx pagefind --source "public" --bundle-dir "pagefind"
```

---

## 🌍 Langues Supportées (14)

| Priorité | Langue | Code |
|----------|--------|------|
| 🔴 TOP | Anglais | `en` |
| 🔴 TOP | Français | `fr` |
| 🔴 TOP | Chinois | `zh` |
| 🔴 TOP | Japonais | `ja` |
| 🔴 TOP | Coréen | `ko` |
| 🟠 HIGH | Allemand | `de` |
| 🟠 HIGH | Espagnol | `es` |
| 🟠 HIGH | Portugais | `pt` |
| 🟠 HIGH | Hindi | `hi` |
| 🟡 MEDIUM | Italien | `it` |
| 🟡 MEDIUM | Néerlandais | `nl` |
| 🟡 MEDIUM | Polonais | `pl` |
| 🟡 MEDIUM | Turc | `tr` |
| 🟡 MEDIUM | Arabe | `ar` |

---

## 📁 Structure du Projet

```
hellobeautyblog/
├── config/                 # Configuration Hugo
│   └── _default/
│       ├── config.yaml     # Config principale
│       ├── languages.yaml  # 14 langues
│       └── params.yaml     # Paramètres & design
├── content/                # Contenu par langue
│   ├── en/
│   ├── fr/
│   └── [autres langues]/
├── themes/hellobeauty/     # Thème personnalisé
│   ├── layouts/            # Templates Hugo
│   └── static/             # CSS, JS, images
├── static/                 # Assets statiques
├── scripts/                # Scripts automatisation
└── data/                   # Données YAML
```

---

## 🎨 Design

**Style: Fresh & Modern**

```css
Primary:    #F8C8DC  /* Rose poudré */
Background: #FDF2F8  /* Rose très clair */
Text:       #1F2937  /* Gris foncé */
Accent:     #6B7280  /* Gris élégant */
```

**Typographie:**
- Titres: Playfair Display
- Corps: Inter
- Accent: Cormorant Garamond

---

## 📝 Créer un Nouveau Produit

### Parfum

```bash
hugo new perfumes/nom-du-parfum.md
```

Structure du fichier:

```yaml
---
title: "Nom du Parfum"
brand: "Marque"
concentration: "Eau de Parfum"
price: "€89"
rating: 4.5

topNotes: ["Note 1", "Note 2"]
heartNotes: ["Note 1", "Note 2"]
baseNotes: ["Note 1", "Note 2"]

longevity: "6-8 hours"
sillage: "Moderate"
season: ["Spring", "Summer"]
occasion: ["Office", "Casual"]

image: "/images/perfumes/nom-du-parfum.jpg"
affiliateUrl: "https://..."
---

Contenu de la description...
```

---

## 🔧 Configuration

### Variables d'Environnement (GitHub Secrets)

```
CLOUDFLARE_API_TOKEN    # Token API Cloudflare
CLOUDFLARE_ACCOUNT_ID   # ID du compte Cloudflare
```

### Affiliation

Configurer dans `config/_default/params.yaml`:

```yaml
affiliation:
  skimlinks:
    enabled: true
    publisherId: "VOTRE_ID"
  amazon:
    enabled: true
    trackingIds:
      us: "tag-us-20"
      fr: "tag-fr-21"
```

---

## 📈 Déploiement

Le site se déploie automatiquement sur Cloudflare Pages à chaque push sur `main`.

### Déploiement Manuel

```bash
# Build
hugo --minify

# Le dossier public/ contient le site prêt à déployer
```

---

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

---

## 📄 License

MIT License - voir [LICENSE](LICENSE)

---

## 📞 Contact

- Website: [hellobeautyblog.com](https://www.hellobeautyblog.com)
- Email: contact@hellobeautyblog.com

---

**Made with 💖 and Hugo**
