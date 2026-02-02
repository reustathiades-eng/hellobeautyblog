# TEMPLATES.md — Templates Hugo du thème hellobeauty
> Dernière mise à jour : 2 février 2026

## Structure des layouts

```
themes/hellobeauty/layouts/
├── _default/
│   ├── baseof.html           # Template de base (head, body wrapper)
│   ├── list.html             # ⭐ Page catégorie (perfumes, skincare...) — TEMPLATE PRINCIPAL
│   └── single.html           # Article générique (blog, etc.)
├── index.html                # ⭐ Homepage — TEMPLATE PRINCIPAL
├── perfumes/single.html      # ⭐ Page produit parfum — TEMPLATE PRINCIPAL
├── partials/
│   ├── header.html           # Navigation + language switcher
│   ├── footer.html           # Footer
│   └── product-card.html     # Carte produit réutilisable
├── authors/
│   ├── list.html             # Page liste auteurs
│   └── single.html           # Page auteur individuel
├── blog/single.html          # Article blog
└── {slug-langue}/single.html # Duplicatas du single parfum pour chaque langue
```

## Templates principaux

### 1. index.html (Homepage)
**Sections** : Hero → Intro SEO → Catégories → New Arrivals → Why Us → Experts → SEO Bottom
- Charge données depuis `data/homepage.json` (intro, bottom)
- Traductions UI hardcodées pour 14 langues
- Floating cards dynamiques (derniers produits par catégorie)

### 2. _default/list.html (Page catégorie)
**Sections** : Hero catégorie → Intro SEO → Sous-catégories → Grille produits → FAQ → SEO Bottom
- Charge données depuis `data/categories/{section}.json`
- La section est détectée via `{{ .Section }}` qui correspond au slug de la langue
- CSS et JS intégrés inline dans le template

### 3. perfumes/single.html (Page produit parfum)
- Carousel images avec thumbnails
- Infos produit (brand, notes, longevity, sillage)
- Contenu article (markdown body)
- Breadcrumb traduit
- **Problème** : Dupliqué pour chaque slug langue (parfums/single.html, parfum/single.html, profumi/single.html, etc.) car Hugo résout le layout par nom de section

### 4. partials/product-card.html
- Composant réutilisable pour afficher un produit dans une grille
- Affiche : image, brand, titre, rating (étoiles), notes preview
- Badges : New, Bestseller (traduits 14 langues)
- Bouton "View" traduit

## Mécanisme de résolution des templates

Hugo cherche le template dans cet ordre :
1. `layouts/{section}/single.html` — ex: `layouts/parfums/single.html` pour un parfum FR
2. `layouts/_default/single.html` — fallback

C'est pourquoi il existe des copies du template single pour chaque slug de section traduit :
- `layouts/perfumes/single.html` (EN)
- `layouts/parfums/single.html` (FR)  
- `layouts/parfum/single.html` (DE, NL, TR)
- `layouts/profumi/single.html` (IT)
- `layouts/perfumy/single.html` (PL)

Idem pour skincare, makeup, haircare avec leurs variantes linguistiques.

## Données disponibles dans les templates

```go
{{ .Language.Lang }}           // "en", "fr", "de"...
{{ .Section }}                 // "perfumes", "parfums", "parfum"...
{{ .Site.Data.categories }}    // Accès aux JSON dans data/categories/
{{ .Site.Data.homepage }}      // Accès au JSON homepage
{{ .Params.family }}           // Frontmatter du contenu
{{ .Site.Menus.main }}         // Menu défini dans languages.yaml
```

## Design

| Élément | Valeur |
|---------|--------|
| Primary | #F8C8DC (rose poudré) |
| Background | #FDF2F8 (rose très clair) |
| Text | #1F2937 (gris foncé) |
| Heading font | Playfair Display |
| Body font | Inter |
| Border radius | 8px (cards: 16-24px) |
