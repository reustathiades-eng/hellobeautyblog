# BRIEF - Génération de fiches parfums HelloBeautyBlog

## FORMAT HUGO FRONT MATTER

```yaml
---
title: "[Nom du parfum] Review: [Sous-titre accrocheur]"
slug: "[nom-parfum-slug]"
description: "[Meta description SEO 150-160 caractères]"
date: [YYYY-MM-DD]
lastmod: 2026-01-30
author: "Emma Collins"
authorSlug: "emma-collins"
categories: ["Perfumes"]
tags: ["[marque]", "[famille olfactive]", "[occasion]"]
keywords: ["[parfum] review", "[marque] perfume", "[mots-clés SEO]"]
images:
  - /images/perfumes/[slug].jpg
featured: false
draft: false

# Product Info
brand: "[Marque]"
productName: "[Nom du produit]"
concentration: "[Eau de Parfum/Eau de Toilette/Parfum]"
gender: "[Women/Men/Unisex]"
price: "€[prix]"
rating: [1-5]

# Fragrance Notes
topNotes:
  - "[Note 1]"
  - "[Note 2]"
heartNotes:
  - "[Note 1]"
  - "[Note 2]"
baseNotes:
  - "[Note 1]"
  - "[Note 2]"

# Characteristics
longevity: "[X-X hours]"
sillage: "[Soft/Moderate/Strong/Enormous]"
season:
  - "[Spring/Summer/Fall/Winter]"
occasion:
  - "[Office/Casual/Evening/Date/Special Occasions]"

translationKey: "[slug-unique]"
---
```

## STRUCTURE DU CONTENU (800-1200 mots)

### 1. Introduction (100-150 mots)
- Accroche personnelle et engageante
- Contexte de création/lancement du parfum
- Pourquoi ce parfum mérite l'attention

### 2. First Impressions / Premières Impressions (100-150 mots)
- Description du flacon et packaging
- Première vaporisation
- Réaction initiale

### 3. The Scent Journey / L'Évolution (200-300 mots)
#### Top Notes
- Description détaillée des notes de tête
- Durée et intensité

#### Heart Notes
- Transition vers le cœur
- Notes dominantes et leur interplay

#### Base Notes
- Le dry-down
- Tenue et évolution finale

### 4. Performance (100-150 mots)
- Longévité réelle (heures testées)
- Sillage (projection)
- Évolution au fil de la journée

### 5. Who Is It For? (100-150 mots)
- Profil de la personne idéale
- Occasions recommandées
- Saisons appropriées
- Tranches d'âge

### 6. The Verdict (100-150 mots)
- Résumé des points forts
- Points faibles éventuels
- Rapport qualité/prix
- Recommandation finale

## STYLE D'ÉCRITURE

- Ton: Professionnel mais accessible, passionné
- Voix: Première personne, expérience personnelle
- Éviter: Jargon trop technique, superlatifs excessifs
- Inclure: Comparaisons concrètes, métaphores sensorielles
- SEO: Mots-clés naturellement intégrés

## CARACTÉRISTIQUES PAR FAMILLE OLFACTIVE

### Floral
- skinType équivalent: "All skin types"
- Occasions typiques: Casual, Office, Date
- Saisons: Spring, Summer

### Oriental/Gourmand
- skinType équivalent: "All skin types"  
- Occasions typiques: Evening, Date, Special Occasions
- Saisons: Fall, Winter

### Woody/Aromatic
- skinType équivalent: "All skin types"
- Occasions typiques: Office, Casual
- Saisons: Fall, Winter, Spring

### Fresh/Aquatic
- skinType équivalent: "All skin types"
- Occasions typiques: Office, Casual, Sport
- Saisons: Spring, Summer

## TRADUCTIONS À PRÉVOIR

Pour chaque parfum, créer les versions dans les 14 langues:
- EN (English) - Version de base
- FR (Français)
- DE (Deutsch)
- ES (Español)
- IT (Italiano)
- PT (Português)
- NL (Nederlands)
- PL (Polski)
- TR (Türkçe)
- JA (日本語)
- KO (한국어)
- ZH (中文)
- AR (العربية)
- HI (हिन्दी)

Chaque traduction doit:
- Adapter le titre et le slug à la langue
- Traduire toutes les notes et caractéristiques
- Conserver le même translationKey
- Adapter les expressions idiomatiques
