# BRIEF - Système de Génération de Fiches Parfums HelloBeautyBlog

## 🎯 Vue d'Ensemble

Ce brief décrit le système professionnel de génération de contenu parfums pour HelloBeautyBlog.com.

**Version:** 2.0
**Dernière mise à jour:** 30 janvier 2026

---

## 📁 Architecture du Système

```
/home/ubuntu/hbb/generation/
├── README.md                          # Documentation complète
├── data/                              # Données JSON des parfums
│   ├── boss-alive.json
│   └── chanel-no5.json
├── scripts/
│   └── generate_perfume.sh            # Script principal
├── templates/
│   ├── perfume_frontmatter.yaml       # Structure YAML de référence
│   └── CONTENT_GENERATION_BRIEF.md    # Brief pour l'API Claude
└── translations/
    ├── perfume_translations.json      # Traductions UI (14 langues)
    └── notes_translations.json        # Notes olfactives (14 langues)
```

---

## 🔑 Principe Fondamental

**Séparation totale entre:**
1. **Front Matter YAML** → Généré localement, format garanti
2. **Contenu Textuel** → Généré par API Claude

Cette séparation élimine les erreurs de format YAML.

---

## 🚀 Utilisation

### Prérequis
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### Générer un parfum (toutes langues)
```bash
./generation/scripts/generate_perfume.sh boss-alive
```

### Générer une langue spécifique
```bash
./generation/scripts/generate_perfume.sh boss-alive fr
```

---

## 📊 Structure des Données Parfum (JSON)

```json
{
  "brand": "Hugo Boss",
  "productName": "Boss Alive",
  "concentration": "Eau de Parfum",
  "price": "89 €",
  "rating": 4.5,
  "launchYear": 2020,
  "perfumer": "Annick Ménardo",
  "family": "Floral Woody",
  "gender": "women",
  
  "longevity": { "min": 6, "max": 8 },
  "sillage": "moderate",
  
  "topNotes": ["apple", "plum", "blackcurrant"],
  "heartNotes": ["jasmine_sambac", "thyme", "olive_blossom"],
  "baseNotes": ["sandalwood", "cedar", "vanilla"],
  
  "seasons": ["spring", "summer", "fall"],
  "occasions": ["office", "casual", "date"],
  
  "images": ["/images/perfumes/boss-alive-swatch.jpg"],
  
  "titles": { "en": "...", "fr": "...", ... },
  "descriptions": { "en": "...", "fr": "...", ... },
  "tags": { "en": [...], "fr": [...], ... },
  "keywords": { "en": [...], "fr": [...], ... }
}
```

---

## 📝 Format YAML Hugo (Obligatoire)

```yaml
---
title: "Boss Alive Review: A Modern Ode to the Authentic Woman"
slug: "boss-alive"
description: "..."
date: 2024-03-15
lastmod: 2026-01-30
author: "Emma Collins"
authorSlug: "emma-collins"
categories:
  - "Perfumes"
tags:
  - "hugo boss"
  - "floral"
keywords:
  - "boss alive review"
images:
  - /images/perfumes/boss-alive-swatch.jpg
  - /images/perfumes/boss-alive.jpg
featured: true
draft: false
brand: "Hugo Boss"
productName: "Boss Alive"
concentration: "Eau de Parfum"
gender: "Women"
price: "89 €"
rating: 4.5
topNotes:
  - "Apple"
  - "Plum"
  - "Blackcurrant"
heartNotes:
  - "Jasmine Sambac"
  - "Thyme"
  - "Olive Blossom"
baseNotes:
  - "Sandalwood"
  - "Cedar"
  - "Vanilla"
longevity: "6-8 hours"
sillage: "Moderate"
season:
  - "Spring"
  - "Summer"
  - "Fall"
occasion:
  - "Office"
  - "Casual"
  - "Date Night"
translationKey: "boss-alive"
---
```

### ⚠️ Règles YAML Critiques

1. **Noms de champs exacts:**
   - `topNotes` (PAS `notes_top` ou `top_notes`)
   - `heartNotes` (PAS `notes_heart`)
   - `baseNotes` (PAS `notes_base`)
   - `season` (PAS `seasons`)
   - `occasion` (PAS `occasions`)

2. **Format des listes:**
   ```yaml
   # ✅ CORRECT
   topNotes:
     - "Apple"
     - "Plum"
   
   # ❌ INCORRECT
   topNotes: ["Apple", "Plum"]
   ```

3. **Guillemets obligatoires** pour les valeurs texte

---

## 🛡️ Mesures Anti-Détection IA

Le brief de génération inclut:

1. **Variation des phrases**
   - Mélanger courtes (5-10 mots) et longues (20-30 mots)
   - Commencer certaines par "Et" ou "Mais"

2. **Ton personnel**
   - Première personne ("Je", "J'ai testé")
   - Anecdotes spécifiques (situations, lieux, moments)

3. **Expressions naturelles**
   - Contractions de la langue cible
   - Idiomes locaux

4. **ÉVITER (détection IA):**
   - "En conclusion" / "Pour conclure"
   - "Il convient de noter"
   - "Plongeons dans" / "Explorons"
   - Répétitions de mots
   - Structures trop régulières

5. **Authenticité**
   - Mentionner 1-2 points négatifs
   - Opinions fortes
   - Comparaisons avec d'autres parfums

---

## 🌍 Langues Supportées

| Code | Langue | Traductions |
|------|--------|-------------|
| en | English | ✅ |
| fr | Français | ✅ |
| de | Deutsch | ✅ |
| es | Español | ✅ |
| it | Italiano | ✅ |
| pt | Português | ✅ |
| nl | Nederlands | ✅ |
| pl | Polski | ✅ |
| tr | Türkçe | ✅ |
| ja | 日本語 | ✅ |
| ko | 한국어 | ✅ |
| zh | 中文 | ✅ |
| ar | العربية | ✅ |
| hi | हिन्दी | ✅ |

---

## 🔧 Ajouter un Nouveau Parfum

1. **Créer le fichier JSON** dans `generation/data/nouveau-parfum.json`
2. **Ajouter les notes manquantes** dans `notes_translations.json`
3. **Exécuter:** `./generation/scripts/generate_perfume.sh nouveau-parfum`
4. **Valider** les fichiers générés
5. **Commit & push**

---

## 📋 Checklist Validation

Avant de push, vérifier pour chaque fichier:

- [ ] `brand` présent et non vide
- [ ] `rating` présent (nombre)
- [ ] `topNotes` avec liste (tirets)
- [ ] `heartNotes` avec liste (tirets)
- [ ] `baseNotes` avec liste (tirets)
- [ ] `season` avec liste (tirets)
- [ ] `occasion` avec liste (tirets)
- [ ] `longevity` présent
- [ ] `sillage` présent
- [ ] `translationKey` identique dans toutes les langues
- [ ] Contenu > 3000 bytes

---

## 🔑 Configuration API

```bash
# Clé API (à exporter avant utilisation)
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Modèle utilisé
MODEL="claude-sonnet-4-5-20250929"

# Temperature (créativité)
TEMPERATURE=0.85
```

La clé est stockée dans `/home/ubuntu/hbb/.env` (non versionné).

---

## 📞 Commande Rapide

```bash
# Générer Boss Alive dans toutes les langues
cd /home/ubuntu/hbb
source .env
./generation/scripts/generate_perfume.sh boss-alive

# Vérifier les fichiers
ls -la content/*/perfumes/boss-alive.md
```
