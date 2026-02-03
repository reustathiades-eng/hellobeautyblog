# PROGRESS.md — État d'avancement du projet
> Dernière mise à jour : 3 février 2026

## ✅ TERMINÉ

### Infrastructure
- [x] Hugo + Cloudflare Pages configuré et fonctionnel
- [x] 14 langues configurées avec slugs traduits
- [x] Thème hellobeauty (Fresh & Modern, rose poudré)
- [x] Domain hellobeautyblog.com actif
- [x] GitHub repo + auto-deploy

### Sous-catégories (199 × 14 langues = 2786 pages)
- [x] Perfumes : 52 sous-catégories (3 gender, 7 family, 32 subfamily, 9 occasion, 1 extra)
- [x] Skincare : 51 sous-catégories (12 product_type, 6 skin_type, 10 concern, 8 ingredient, 15 brand)
- [x] Makeup : 51 sous-catégories (20 product_type, 5 zone, 5 finish, 3 coverage, 3 skin_type, 15 brand)
- [x] Haircare : 46 sous-catégories (12 product_type, 8 hair_type, 11 concern, 15 brand)
- [x] Toutes les sous-catégories ont des URLs traduites dans les 14 langues
- [x] Contenu SEO (seo_title, intro, FAQ, seo_bottom) généré via API Claude

### Traductions (3 février 2026)
- [x] 1911 titres/descriptions sous-catégories traduits
- [x] 1085 slugs d'URL traduits (ex: /fr/soins/anti-age/)
- [x] JSONs data/categories/ synchronisés avec les nouveaux slugs

### Contenu existant (59 articles)
- [x] 13 parfums complets (14 langues = 182 pages)
- [x] 11 articles skincare EN
- [x] 30 articles makeup EN
- [x] 5 articles haircare EN
- [x] 4 bios auteurs (14 langues = 56 pages)
- [x] 58 images parfums

### SEO global
- [x] Textes SEO homepage (14 langues)
- [x] SEO data JSON par catégorie × 14 langues

### Listes de produits à générer (Étape 1 FAITE)
- [x] Perfumes : 511 produits listés → /home/ubuntu/hbb/generation/product_lists/perfumes.json
- [x] Skincare : 278 produits listés → /home/ubuntu/hbb/generation/product_lists/skincare.json
- [x] Makeup : 500 produits listés → /home/ubuntu/hbb/generation/product_lists/makeup.json
- [x] Haircare : 270 produits listés → /home/ubuntu/hbb/generation/product_lists/haircare.json
- [x] Gaps : 70 produits pour combler sous-catégories < 3 → /home/ubuntu/hbb/generation/product_lists/gaps.json
- [x] TOTAL : 1 629 produits avec caractéristiques (brand, name, slug, subcategories)
- [x] Vérification couverture : au moins 3 produits par sous-catégorie

---

## 🟡 EN COURS / PROCHAINE ÉTAPE

### Étape 2 : Interface de saisie des URLs images + Génération fiches

**Workflow :**
1. ✅ Lister les 1629 produits (FAIT)
2. ✅ Déterminer caractéristiques JSON (FAIT)
3. ⏳ **Créer interface pour renseigner jusqu'à 4 URLs d'images par produit**
4. ⏳ Télécharger les images sur le serveur
5. ⏳ Générer les fiches Hugo en 14 langues via API Claude
6. ⏳ Git push → deploy Cloudflare

**Interface requise :**
- Afficher les 1629 produits (filtrable par catégorie)
- Champ pour renseigner jusqu'à 4 URLs d'images par produit
- Bouton de validation
- Export JSON pour lancer la génération
- Afficher 100 produits par page

**Structure JSON produit :**
```json
{
  "brand": "Chanel",
  "name": "No. 5",
  "slug": "chanel-no-5",
  "gender": "women",
  "subcategories": ["women", "floral", "floral-aldehyde", "evening", "romantic"]
}
```

### Fichiers clés
- Listes produits : /home/ubuntu/hbb/generation/product_lists/
- Script génération : /home/ubuntu/hbb/generation/generate_product_lists.py
- API key : /home/ubuntu/hbb/.secrets
- Template produit : themes/hellobeauty/layouts/_default/single.html

---

## ⏳ À FAIRE (après les 1629 produits)

### Monétisation
- [ ] Intégrer Skimlinks
- [ ] Configurer Amazon Associates (multi-pays)
- [ ] Intégrer Awin (Sephora, Douglas, Notino)

### Technique
- [ ] Pipeline automatique (scrape → generate → deploy)
- [ ] Analytics (Google Analytics ou Plausible)
- [ ] Sitemap optimization

### Design
- [ ] Dark mode (optionnel)
- [ ] Recherche Pagefind
- [ ] Newsletter (Formspree)

---

## 📊 RÉCAPITULATIF SOUS-CATÉGORIES

### Perfumes (52 sous-catégories)
| Type | Nb | Slugs |
|------|-----|-------|
| gender | 3 | women, men, unisex |
| family | 7 | floral, oriental, woody, fresh, aromatic, chypre, gourmand |
| subfamily | 32 | floral-fruity, floral-white, ... gourmand-chocolate |
| occasion | 9 | everyday, evening, romantic, office, summer, winter, wedding, sport, travel |
| extra | 1 | |

### Skincare (51 sous-catégories)
| Type | Nb | Slugs |
|------|-----|-------|
| product_type | 12 | cleanser, toner, serum, essence, moisturizer, eye-cream, sunscreen, mask, exfoliator, oil, mist, spot-treatment |
| skin_type | 6 | oily, dry, combination, sensitive, normal, mature |
| concern | 10 | anti-aging, acne, hydration, brightening, dark-spots, pores, redness, wrinkles, dark-circles, firmness |
| ingredient | 8 | retinol, vitamin-c, hyaluronic-acid, niacinamide, salicylic-acid, glycolic-acid, peptides, ceramides |
| brand | 15 | cerave, la-roche-posay, the-ordinary, neutrogena, clinique, olay, kiehls, drunk-elephant, tatcha, glow-recipe, paulas-choice, sk-ii, estee-lauder, lancome, vichy |

### Makeup (51 sous-catégories)
| Type | Nb | Slugs |
|------|-----|-------|
| product_type | 20 | foundation, concealer, primer, powder, blush, bronzer, contour, highlighter, setting-spray, mascara, eyeliner, eyeshadow, eye-primer, brows, false-lashes, lipstick, lip-gloss, lip-liner, lip-balm, nail-polish |
| zone | 5 | face, eyes, lips, brows, nails |
| finish | 5 | matte, dewy, satin, shimmer, natural |
| coverage | 3 | light-coverage, medium-coverage, full-coverage |
| skin_type | 3 | oily-skin, dry-skin, sensitive-skin |
| brand | 15 | mac, maybelline, nars, fenty-beauty, charlotte-tilbury, rare-beauty, huda-beauty, urban-decay, too-faced, nyx, elf, tarte, dior-beauty, chanel-beauty, bobbi-brown |

### Haircare (46 sous-catégories)
| Type | Nb | Slugs |
|------|-----|-------|
| product_type | 12 | shampoo, conditioner, hair-mask, hair-oil, leave-in, serum, dry-shampoo, heat-protection, styling-cream, styling-gel, hair-spray, scalp-treatment |
| hair_type | 8 | fine-hair, thick-hair, curly-hair, wavy-hair, straight-hair, coily-hair, color-treated, natural-hair |
| concern | 11 | volume, repair, hydration, frizz, dandruff, color-protection, hair-growth, thinning, split-ends, shine, scalp-health |
| brand | 15 | kerastase, olaplex, moroccanoil, redken, loreal-professionnel, pantene, tresemme, aveda, k18, gisou, garnier, john-frieda, bumble-and-bumble, living-proof, briogeo |

### Totaux
| Section | Types | Sous-cat | Pages (×14 langues) |
|---------|-------|----------|---------------------|
| Perfumes | 4 | 52 | 728 |
| Skincare | 5 | 51 | 714 |
| Makeup | 6 | 51 | 714 |
| Haircare | 4 | 46 | 644 |
| **TOTAL** | **19** | **200** | **2 800** |

### Produits à générer
| Catégorie | Produits listés | Existants | À générer |
|-----------|----------------|-----------|-----------|
| Perfumes | 511 | 13 | 498 |
| Skincare | 278 | 11 | 267 |
| Makeup | 500 | 30 | 470 |
| Haircare | 270 | 5 | 265 |
| Gaps | 70 | 0 | 70 |
| **TOTAL** | **1 629** | **59** | **1 570** |

---

## ⚠️ NOTES TECHNIQUES

### MCP SSH (olfapedia:exec)
- Timeout 60s → toujours nohup + background pour les commandes longues
- Petites commandes pour éviter les timeouts

### Hugo
- theme: "hellobeauty" OBLIGATOIRE dans config.yaml
- defaultContentLanguageInSubdir: true OBLIGATOIRE
- Le champ url: dans frontmatter override le slug du dossier

### Cloudflare Pages
- Build timeout : 20 min max
- Un build stuck bloque toute la queue → annuler manuellement
