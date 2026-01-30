# 🧪 Système de Génération de Contenu - HelloBeautyBlog

## 📋 Vue d'Ensemble

Ce système génère automatiquement des fiches parfums complètes dans 14 langues en utilisant l'API Claude Sonnet 4.5.

**Principe clé:** Séparation totale entre le **front matter YAML** (fixe, généré localement) et le **contenu textuel** (généré par l'API).

Cette séparation garantit:
- ✅ Format YAML toujours correct
- ✅ Tous les champs obligatoires présents
- ✅ Traductions exactes des notes, saisons, occasions
- ✅ Cohérence entre toutes les langues

## 📁 Structure

```
generation/
├── README.md                          # Ce fichier
├── data/                              # Données des parfums (JSON)
│   ├── boss-alive.json
│   └── chanel-no5.json
├── scripts/                           # Scripts de génération
│   └── generate_perfume.sh            # Script principal
├── templates/                         # Templates et briefs
│   ├── perfume_frontmatter.yaml       # Structure YAML
│   └── CONTENT_GENERATION_BRIEF.md    # Brief pour l'API
└── translations/                      # Fichiers de traduction
    ├── perfume_translations.json      # Traductions UI
    └── notes_translations.json        # Traductions notes olfactives
```

## 🚀 Utilisation

### Générer un parfum dans toutes les langues
```bash
./generation/scripts/generate_perfume.sh boss-alive
```

### Générer un parfum dans une langue spécifique
```bash
./generation/scripts/generate_perfume.sh boss-alive fr
```

### Ajouter un nouveau parfum

1. **Créer le fichier de données** dans `generation/data/nouveau-parfum.json`
2. **Ajouter les traductions manquantes** dans `notes_translations.json`
3. **Exécuter le script** de génération

## 📊 Structure des Données Parfum

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
  
  "images": ["/images/perfumes/boss-alive-swatch.jpg", "/images/perfumes/boss-alive.jpg"],
  
  "titles": { "en": "...", "fr": "...", ... },
  "descriptions": { "en": "...", "fr": "...", ... },
  "tags": { "en": [...], "fr": [...], ... },
  "keywords": { "en": [...], "fr": [...], ... }
}
```

## 🌍 Langues Supportées

| Code | Langue | Statut |
|------|--------|--------|
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

## 🛡️ Mesures Anti-Détection IA

Le brief de génération inclut des instructions spécifiques pour:
- Varier la longueur des phrases
- Utiliser des contractions naturelles
- Inclure des anecdotes personnelles
- Éviter les phrases typiques de l'IA
- Exprimer des opinions authentiques

## ⚠️ Points d'Attention

1. **Ne jamais modifier les noms de champs YAML**
   - `topNotes` (pas `notes_top`)
   - `season` (pas `seasons`)
   - `occasion` (pas `occasions`)

2. **Format des listes YAML**
   ```yaml
   # CORRECT
   topNotes:
     - "Apple"
     - "Plum"
   
   # INCORRECT
   topNotes: ["Apple", "Plum"]
   ```

3. **Toujours valider après génération**
   - Le script affiche un résumé de validation
   - Vérifier manuellement les fichiers si nécessaire

## 🔑 Configuration API

La clé API Anthropic est stockée dans:
- `/home/ubuntu/hbb/.env`
- Variable dans le script

**Modèle utilisé:** `claude-sonnet-4-5-20250929`
**Temperature:** 0.85 (pour plus de créativité)

## 📝 Mise à Jour

Dernière mise à jour: 30 janvier 2026
Version: 2.0
