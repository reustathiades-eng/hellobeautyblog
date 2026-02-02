# TRANSLATION RULES — HelloBeautyBlog
> Règles OBLIGATOIRES pour que le language switcher fonctionne

## Règle fondamentale

Hugo lie les pages entre langues de 2 façons :
1. **Même chemin de fichier** (ex: `/en/blog/post.md` ↔ `/fr/blog/post.md`)
2. **`translationKey`** (OBLIGATOIRE quand les chemins diffèrent entre langues)

Comme nos catégories utilisent des slugs traduits (`/en/perfumes/` ↔ `/fr/parfums/`),
le `translationKey` est **TOUJOURS obligatoire** sauf pour `blog/` (même slug partout).

---

## Checklist pour CHAQUE nouveau contenu

### 1. Page de catégorie (_index.md)
```yaml
---
title: "Parfums"
description: "..."
translationKey: "section-perfumes"   # ← OBLIGATOIRE, identique dans les 14 langues
---
```

Keys de référence pour les catégories :
- `section-perfumes`
- `section-skincare`
- `section-makeup`
- `section-haircare`
- `section-blog`
- `section-brands`
- `section-guides`

### 2. Sous-catégorie (_index.md)
```yaml
---
title: "Parfums Femme"
translationKey: "perfumes-women"     # ← OBLIGATOIRE
url: "/fr/parfums/femme/"            # ← OBLIGATOIRE (URL traduite explicite)
subcategory_type: "gender"
subcategory_value: "Women"
---
```

### 3. Produit (perfume .md)
```yaml
---
title: "Coco Mademoiselle"
translationKey: "coco-mademoiselle"  # ← OBLIGATOIRE, identique 14 langues
---
```

### 4. Article (skincare/makeup/haircare/blog .md)
```yaml
---
title: "Mon article"
translationKey: "mon-article-key"    # ← OBLIGATOIRE si traduit dans d'autres langues
---
```

---

## Récap : quand le switcher fonctionne / ne fonctionne pas

| Situation | Switcher | Pourquoi |
|-----------|----------|----------|
| Même chemin + même nom de fichier | ✅ Auto | Hugo détecte automatiquement |
| Chemins différents + `translationKey` identique | ✅ OK | Hugo lie via la clé |
| Chemins différents + PAS de `translationKey` | ❌ CASSÉ | Hugo ne peut pas lier |
| `translationKey` présent EN mais pas FR | ❌ CASSÉ | La clé doit être dans TOUTES les langues |
| Article EN sans traduction | ℹ️ Pas de switcher | Normal, il n'y a rien à lier |

---

## Vérification rapide

```bash
# Trouver les _index.md SANS translationKey (potentiel bug)
find content/ -name "_index.md" -exec sh -c 'grep -qL "translationKey" "$1" && echo "❌ $1"' _ {} \;

# Vérifier qu'une clé existe dans toutes les langues
grep -rl 'translationKey: "section-perfumes"' content/
```
