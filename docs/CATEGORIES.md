# CATEGORIES.md — Catégories et sous-catégories
> Dernière mise à jour : 2 février 2026

## Structure des catégories

Le site a 4 catégories principales, chacune avec des sous-catégories physiques (pages dédiées).

---

## 1. PERFUMES

### Sous-catégories par Gender (3 pages)
| Slug | Label EN |
|------|----------|
| women | Women's Perfumes |
| men | Men's Perfumes |
| unisex | Unisex Perfumes |

> ⚠️ Les parfums Unisex doivent aussi apparaître dans Women et Men.

### Sous-catégories par Family — Niveau 1 (7 pages)
Basé sur Michael Edwards' Fragrance Wheel + Gourmand.

| Slug | Label EN | Emoji |
|------|----------|-------|
| floral | Floral | 🌸 |
| oriental | Oriental | 🌙 |
| woody | Woody | 🌲 |
| fresh | Fresh | 🍃 |
| aromatic | Aromatic | 🌿 |
| chypre | Chypre | 🍂 |
| gourmand | Gourmand | 🍫 |

### Sous-catégories par Subfamily — Niveau 2 (32 pages)
Chaque sous-famille est une page physique à part entière (pas un filtre).

| Family | Subfamilies |
|--------|-------------|
| floral | floral-fruity, floral-white, floral-powdery, floral-green, floral-aldehyde, floral-aquatic |
| oriental | oriental-spicy, oriental-vanilla, oriental-amber, oriental-woody, oriental-floral |
| woody | woody-aromatic, woody-spicy, woody-dry, woody-mossy, woody-earthy |
| fresh | fresh-citrus, fresh-aquatic, fresh-green, fresh-ozonic, fresh-fruity |
| aromatic | aromatic-fougere, aromatic-herbal, aromatic-spicy, aromatic-marine |
| chypre | chypre-fruity, chypre-floral, chypre-leather, chypre-green |
| gourmand | gourmand-vanilla, gourmand-sweet, gourmand-coffee, gourmand-chocolate |

### Sous-catégories par Occasion (9 pages)

| Slug | Label EN | Emoji |
|------|----------|-------|
| everyday | Everyday Perfumes | ☀️ |
| evening | Evening Perfumes | 🌃 |
| romantic | Romantic Perfumes | 💕 |
| office | Office Perfumes | 💼 |
| summer | Summer Perfumes | 🏖️ |
| winter | Winter Perfumes | ❄️ |
| wedding | Wedding Perfumes | 💒 |
| sport | Sport Perfumes | 🏃 |
| travel | Travel Perfumes | ✈️ |

### Total perfumes : 51 sous-catégories × 14 langues = 714 pages

---

## 2. SKINCARE (À implémenter)

### Par type de peau (5)
dry, oily, combination, sensitive, normal

### Par routine (6)
cleanser, toner, serum, moisturizer, eye-cream, sunscreen

### Par concern (5)
anti-aging, acne, dark-spots, redness, hydration

### Total skincare : 16 sous-catégories × 14 langues = 224 pages

---

## 3. MAKEUP (À implémenter)

### Face (5)
foundation, concealer, powder, blush, bronzer

### Eyes (4)
eyeshadow, eyeliner, mascara, eyebrow

### Lips (3)
lipstick, lip-gloss, lip-liner

### Nails (2)
nail-polish, nail-care

### Total makeup : 14 sous-catégories × 14 langues = 196 pages

---

## 4. HAIRCARE (À implémenter)

### Par type de cheveux (5)
straight, wavy, curly, coily, fine

### Par concern (5)
hair-loss, dandruff, frizz, damage-repair, color-protection

### Total haircare : 10 sous-catégories × 14 langues = 140 pages

---

## TOTAL GLOBAL

| Catégorie | Sous-catégories | × 14 langues |
|-----------|----------------|--------------|
| Perfumes | 51 | 714 |
| Skincare | 16 | 224 |
| Makeup | 14 | 196 |
| Haircare | 10 | 140 |
| **Total** | **91** | **1 274** |

---

## Implémentation technique (en cours)

Chaque sous-catégorie = un dossier avec `_index.md` dans Hugo :
```
content/en/perfumes/floral/_index.md
content/en/perfumes/floral-fruity/_index.md
content/en/perfumes/women/_index.md
content/fr/parfums/floral/_index.md
...
```

Le template `list.html` détecte si c'est une sous-catégorie et filtre les produits via les champs frontmatter (family, subfamily, gender, occasion).

Les données SEO (intro, FAQ) pour chaque sous-catégorie seront générées via l'API Claude et stockées soit dans le frontmatter des _index.md, soit dans des fichiers data/subcategories/ JSON.
