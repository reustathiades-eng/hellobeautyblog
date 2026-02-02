# TRANSLATION RULES — HelloBeautyBlog
> Règles OBLIGATOIRES pour que le language switcher fonctionne
> **LIRE AVANT TOUTE CRÉATION DE CONTENU OU DE SCRIPT**

## Règle n°1 : TOUT contenu DOIT avoir un `translationKey`

```yaml
translationKey: "ma-cle-unique"  # OBLIGATOIRE dans CHAQUE fichier .md
```

- La clé doit être **identique dans les 14 langues**
- La clé doit être **unique par contenu** (pas de doublon entre 2 articles différents)
- Sans translationKey → le language switcher NE FONCTIONNE PAS

## Règle n°2 : Toujours créer dans les 14 langues

Quand on crée un nouveau contenu (produit, article, sous-catégorie), il faut
le créer dans **les 14 langues en même temps**. Un article EN-only = pas de switcher.

Langues : en, fr, de, es, it, pt, nl, pl, tr, ja, ko, zh, ar, hi

## Règle n°3 : Dossiers traduits = `url:` explicite obligatoire

Quand le dossier change entre langues (ex: `en/perfumes/` vs `fr/parfums/`),
il faut ajouter une `url:` explicite dans le frontmatter :

```yaml
url: "/fr/parfums/femme/"  # OBLIGATOIRE quand le chemin diffère de EN
```

---

## Convention des translationKey par type

### Catégorie principale (_index.md)
```
translationKey: "section-{nom}"
```
Valeurs existantes : `section-perfumes`, `section-skincare`, `section-makeup`, `section-haircare`, `section-blog`, `section-brands`, `section-guides`

### Produit parfum
```
translationKey: "{slug-produit}"
```
Exemples : `coco-mademoiselle`, `dior-sauvage`, `black-opium`

### Sous-catégorie parfum
```
translationKey: "perfumes-{value}"
```
Exemples : `perfumes-women`, `perfumes-floral`, `perfumes-evening`

### Article (skincare/makeup/haircare/blog)
```
translationKey: "{slug-en-de-l-article}"
```
Exemples : `benefit-stay-dont-stray-review`, `caudalie-premier-cru-eye-cream`

---

## Frontmatter minimal par type

### Produit parfum
```yaml
---
title: "Coco Mademoiselle"
translationKey: "coco-mademoiselle"
slug: "coco-mademoiselle"
brand: "Chanel"
# ... autres champs
---
```

### Article traduit
```yaml
---
title: "Benefit Stay Don't Stray - Avis"
translationKey: "benefit-stay-dont-stray-review"
slug: "benefit-stay-dont-stray-avis"
# ... autres champs
---
```

### Sous-catégorie
```yaml
---
title: "Parfums Femme"
translationKey: "perfumes-women"
url: "/fr/parfums/femme/"
subcategory_type: "gender"
subcategory_value: "Women"
---
```

---

## Validation

Lancer après chaque création de contenu :
```bash
bash /home/ubuntu/hbb/scripts/validate_translations.sh
```

---

## Erreurs fréquentes à éviter

| Erreur | Conséquence | Solution |
|--------|-------------|----------|
| Pas de `translationKey` | Switcher cassé | Toujours ajouter la clé |
| Clé différente entre langues | Switcher cassé | Copier-coller la même clé |
| Clé dupliquée (2 articles avec même clé) | Hugo mélange les pages | Vérifier unicité |
| Article créé en EN seulement | Pas de switcher | Créer dans les 14 langues |
| Dossier traduit sans `url:` | URL incorrecte | Ajouter `url:` explicite |
