# DATA_STRUCTURE.md — Où sont stockées les données
> Dernière mise à jour : 2 février 2026

## Vue d'ensemble des sources de données

Le site utilise 3 types de stockage de données :

| Type | Emplacement | Usage |
|------|-------------|-------|
| **Frontmatter** | `content/{lang}/{section}/{slug}.md` | Données produit (notes, prix, rating, family...) |
| **Data JSON** | `data/` | SEO catégories, textes homepage, sous-catégories |
| **Templates** | `themes/hellobeauty/layouts/` | Traductions UI hardcodées dans les templates |

---

## 1. Frontmatter produit (fichiers .md)

### Parfum — Champs disponibles

```yaml
title: "Titre SEO complet"
slug: "black-opium"                    # Identique dans toutes les langues
description: "Meta description SEO"
date: 2024-02-05
lastmod: 2026-01-30
author: "Emma Collins"
authorSlug: "emma-collins"
categories: ["Perfumes"]               # Traduit par langue (Parfums, Profumi...)
tags: ["ysl", "coffee", "vanilla"]
keywords: ["black opium review"]
images:                                # ORDRE CRITIQUE :
  - /images/perfumes/black-opium-swatch.jpg    # 1. Swatch (couleur jus) EN PREMIER
  - /images/perfumes/black-opium.jpg           # 2. Bottle
  - /images/perfumes/black-opium-2.jpg         # 3. Detail
featured: true
draft: false
brand: "Yves Saint Laurent"
productName: "Black Opium"
concentration: "Eau de Parfum"
gender: "Women"                        # Women | Men | Unisex
family: "oriental"                     # Famille olfactive (7 familles)
subfamily: "oriental-vanilla"          # Sous-famille (32 sous-familles)
occasion:                              # Multi-select (9 occasions possibles)
  - "Evening"
  - "Winter"
  - "Romantic"
price: "100 €"
rating: 4.5
topNotes: ["Pink Pepper", "Orange Blossom"]
heartNotes: ["Coffee", "Jasmine"]
baseNotes: ["Vanilla", "Patchouli"]
longevity: "6-9 hours"
sillage: "Strong"
season: ["Fall", "Winter"]
translationKey: "black-opium"          # Lie les traductions entre langues
```

### Taxonomies produit

**Gender** : Women, Men, Unisex
- Les produits Unisex doivent aussi remonter dans Women et Men

**Family** (7 familles — Michael Edwards Fragrance Wheel + Gourmand) :
floral, oriental, woody, fresh, aromatic, chypre, gourmand

**Subfamily** (32 sous-familles) :
- floral: floral-fruity, floral-white, floral-powdery, floral-green, floral-aldehyde, floral-aquatic
- oriental: oriental-spicy, oriental-vanilla, oriental-amber, oriental-woody, oriental-floral
- woody: woody-aromatic, woody-spicy, woody-dry, woody-mossy, woody-earthy
- fresh: fresh-citrus, fresh-aquatic, fresh-green, fresh-ozonic, fresh-fruity
- aromatic: aromatic-fougere, aromatic-herbal, aromatic-spicy, aromatic-marine
- chypre: chypre-fruity, chypre-floral, chypre-leather, chypre-green
- gourmand: gourmand-vanilla, gourmand-sweet, gourmand-coffee, gourmand-chocolate

**Occasion** (9 occasions) :
Everyday, Evening, Romantic, Office, Summer, Winter, Wedding, Sport, Travel

### Attribution des 13 parfums existants

| Parfum | Family | Subfamily | Gender | Occasions |
|--------|--------|-----------|--------|-----------|
| Boss Alive | fresh | fresh-green | Women | Everyday, Office, Summer |
| Chanel N°5 | floral | floral-aldehyde | Women | Evening, Wedding, Winter |
| Miss Dior | floral | floral-fruity | Women | Everyday, Romantic, Wedding |
| J'adore | floral | floral-white | Women | Evening, Wedding, Romantic |
| La Vie Est Belle | floral | floral-fruity | Women | Everyday, Romantic, Office |
| Black Opium | oriental | oriental-vanilla | Women | Evening, Winter, Romantic |
| Coco Mademoiselle | oriental | oriental-floral | Women | Everyday, Office, Travel |
| Good Girl | oriental | oriental-spicy | Women | Evening, Romantic, Winter |
| Guerlain Shalimar | oriental | oriental-amber | Women | Evening, Winter, Wedding |
| Bleu de Chanel | woody | woody-aromatic | Men | Everyday, Office, Travel |
| Dior Sauvage | woody | woody-spicy | Men | Everyday, Office, Sport |
| Acqua di Gio | fresh | fresh-aquatic | Men | Everyday, Summer, Sport |
| 1 Million | woody | woody-spicy | Men | Evening, Romantic, Winter |

---

## 2. Data JSON (data/)

### data/homepage.json
```json
{
  "intro": { "en": "texte SEO intro...", "fr": "...", ... },
  "bottom": { "en": "texte SEO bottom...", "fr": "...", ... }
}
```
Utilisé par : `themes/hellobeauty/layouts/index.html`

### data/categories/{section}.json
Structure identique pour perfumes.json, skincare.json, makeup.json, haircare.json :
```json
{
  "en": {
    "intro_title": "...",
    "intro": "texte 40 mots",
    "subcategories": {
      "group_key": {
        "title": "Shop by ...",
        "items": [
          { "name": "Floral", "emoji": "🌸", "url": "/en/perfumes/?family=floral" }
        ]
      }
    },
    "faq": [
      { "question": "...", "answer": "..." }
    ],
    "seo_title": "...",
    "seo_bottom": "texte 40 mots"
  },
  "fr": { ... },
  ...14 langues
}
```
Utilisé par : `themes/hellobeauty/layouts/_default/list.html`

> ⚠️ Les URLs dans subcategories pointent actuellement vers des filtres (?family=). 
> Phase en cours : les transformer en vraies sous-catégories physiques (/en/perfumes/floral/).

---

## 3. Traductions UI dans les templates

Les traductions de l'interface (boutons, labels, titres de section) sont hardcodées dans les templates Hugo avec des blocs `{{ if eq $lang "fr" }}...{{ end }}`.

Fichiers concernés :
- `layouts/index.html` — Homepage (hero, categories, why us, experts)
- `layouts/_default/list.html` — Pages catégories (toolbar, pagination, FAQ)
- `layouts/perfumes/single.html` — Page produit parfum (breadcrumb, labels)
- `layouts/partials/product-card.html` — Carte produit (badges, bouton view)
- `layouts/partials/header.html` — Navigation, language switcher
- `layouts/partials/footer.html` — Footer

---

## 4. Images

```
static/images/
├── perfumes/     # 58 images : {slug}-swatch.jpg, {slug}.jpg, {slug}-2.jpg, {slug}-3.jpg
├── skincare/     # Images articles skincare
├── makeup/       # Images articles makeup
├── haircare/     # Images articles haircare
├── blog/         # Images articles blog
├── authors/      # 4 photos : sophie-laurent.webp, emma-chen.webp, isabella-romano.webp, olivia-taylor.webp
├── categories/   # 4 images : perfumes.webp, skincare.webp, makeup.webp, haircare.webp
├── hero/         # hero-main.webp, floating-perfume.webp, floating-skincare.webp
└── icons/        # icon-perfumes.webp, icon-skincare.webp, icon-makeup.webp, icon-haircare.webp
```

### Règle d'ordre images parfums
1. `{slug}-swatch.jpg` — Couleur du jus (TOUJOURS EN PREMIER dans frontmatter)
2. `{slug}.jpg` — Photo bouteille principale
3. `{slug}-2.jpg` — Détail 2
4. `{slug}-3.jpg` — Détail 3
