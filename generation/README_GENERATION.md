# 📝 HelloBeautyBlog - Content Generation Guide

## 📊 Contenu à générer

### Homepage SEO (28 textes)
| Section | Description | Longueur |
|---------|-------------|----------|
| **Intro** | Paragraphe d'accueil | 2-3 phrases (~50 mots) |
| **Bottom** | Texte "About" SEO | 200-250 mots |

**× 14 langues = 28 textes**

### Author Bios (56 textes)
| Auteur | Spécialité | Ville |
|--------|------------|-------|
| Sophie Laurent | Parfums | Paris/Grasse |
| Emma Chen | Skincare | Seoul |
| Isabella Romano | Makeup | Milan |
| Olivia Taylor | Haircare | London |

**× 14 langues = 56 textes (300-400 mots chacun)**

---

## 🚀 Utilisation

### 1. Configurer l'API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
```

### 2. Générer le contenu

```bash
cd /home/ubuntu/hbb/generation

# Générer tout
python generate_content.py all

# Ou séparément
python generate_content.py homepage
python generate_content.py authors
```

### 3. Intégrer dans Hugo

```bash
python integrate_content.py all
```

### 4. Commit et deploy

```bash
cd /home/ubuntu/hbb
git add .
git commit -m "ADD: Generated SEO content and author bios (14 languages)"
git push origin main
```

---

## 📋 BRIEFS DÉTAILLÉS

### HOMEPAGE INTRO (par langue)

**Objectif**: Accueillir les visiteurs en 2-3 phrases max.

**Éléments obligatoires**:
- Message de bienvenue chaleureux
- Mention des 4 catégories (parfums, soins, maquillage, cheveux)
- Promesse d'avis d'experts honnêtes

**Ton**: Chaleureux, expert mais accessible, moderne

**Exemple EN** (à ne pas copier):
> "Welcome to your trusted destination for beauty discoveries. Our team of experts shares honest reviews across perfumes, skincare, makeup and haircare to help you find products that truly work for you."

---

### HOMEPAGE BOTTOM SEO (par langue)

**Objectif**: Texte "About" optimisé SEO pour le bas de page.

**Structure** (5 parties):
1. **Mission** (2-3 phrases): Qui sommes-nous, notre raison d'être
2. **Notre équipe** (2-3 phrases): 4 experts avec vraies spécialités
3. **Notre contenu** (2-3 phrases): Reviews, guides, conseils
4. **Nos valeurs** (2-3 phrases): Indépendance, honnêteté, vrais tests
5. **Invitation** (1-2 phrases): Appel à explorer le blog

**Mots-clés à intégrer naturellement**:
- beauty blog, perfume reviews, skincare advice
- makeup tips, haircare guide, honest reviews
- expert recommendations, independent beauty
- luxury beauty, best perfumes, skincare routine

**Longueur**: 200-250 mots

---

### AUTHOR BIOS (par auteur × par langue)

**Objectif**: Biographie professionnelle engageante (300-400 mots)

**Structure**:

1. **ACCROCHE** (2-3 phrases)
   - Ce qui anime leur passion
   - Moment déclencheur ou philosophie personnelle

2. **PARCOURS** (1 paragraphe)
   - Formation précise (écoles, diplômes)
   - Postes occupés (entreprises connues)
   - Réalisations notables

3. **EXPERTISE** (1 paragraphe)
   - Ce qui rend leur approche unique
   - Leur philosophie professionnelle
   - Domaines de spécialisation

4. **CHEZ HELLOBEAUTYBLOG** (2-3 phrases)
   - Leur rôle sur le blog
   - Type de contenu qu'ils créent
   - Ce que les lecteurs peuvent attendre

5. **TOUCHE PERSONNELLE** (2-3 phrases)
   - Catégorie de produits favorite
   - Activité hors travail
   - Fun fact

**Ton**: Professionnel mais chaleureux, 3ème personne, expertise sans arrogance

---

## 👤 PROFILS AUTEURS DÉTAILLÉS

### Sophie Laurent - Perfume Expert

**Background**:
- Française, ~35 ans
- ISIPCA Versailles (école de parfumerie)
- Master Chimie des Parfums, Institut de Grasse
- Ex-évaluatrice chez Givaudan
- Conférencière au Cinquième Sens Paris

**Spécialités**:
- Parfums de niche
- Parfumerie française traditionnelle
- Analyse olfactive
- Parfums vintage
- Matières premières naturelles

**Personnalité**:
- Sophistiquée et passionnée
- Parle poétiquement des parfums
- Aime l'histoire de la parfumerie
- Collectionne les flacons vintage

---

### Emma Chen - Skincare Specialist

**Background**:
- Coréenne-Américaine, ~32 ans
- MD Dermatologie, Seoul National University
- Certificat CIDESCO (formulation cosmétique)
- Ex-consultante R&D chez Amorepacific
- Contributrice Allure et Vogue Beauty

**Spécialités**:
- K-Beauty et J-Beauty
- Ingrédients actifs (rétinol, niacinamide, etc.)
- Peaux sensibles et réactives
- Barrière cutanée
- Anti-âge préventif

**Personnalité**:
- Scientifique mais accessible
- Obsédée par les listes d'ingrédients
- Prône les routines douces
- Teste tout sur elle-même

---

### Isabella Romano - Makeup Artist

**Background**:
- Italienne, ~40 ans
- Accademia del Lusso Milan
- Certifiée MAC Pro
- Lead Artist Milan Fashion Week (2018-2024)
- Travaillé pour Vogue Italia, Elle

**Spécialités**:
- Maquillage éditorial
- Looks défilé et red carpet
- Beauté nuptiale
- Théorie des couleurs
- Beauté inclusive

**Personnalité**:
- Créative et audacieuse
- Aime expérimenter les couleurs
- Milite pour la diversité
- Généreuse en conseils

---

### Olivia Taylor - Haircare Expert

**Background**:
- Britannique, ~38 ans
- Trichologie certifiée IAT London
- Diplôme avancé Vidal Sassoon Academy
- Consultante Olaplex Professional
- Auteure "The Scalp Solution" (2023)

**Spécialités**:
- Santé du cuir chevelu
- Soins naturels
- Cheveux bouclés (méthode Curly Girl)
- Réparation capillaire
- Coloration et entretien

**Personnalité**:
- Chaleureuse et maternelle
- Croit que tout part du cuir chevelu
- Passionnée par les formulations clean
- Très pédagogue

---

## 📁 Fichiers générés

Après exécution, les fichiers suivants sont créés :

```
generation/
├── homepage_content.json    # Textes homepage (intro + bottom × 14 langues)
└── author_bios.json         # Bios auteurs (4 × 14 langues)
```

Ces fichiers JSON sont ensuite intégrés par `integrate_content.py`.

---

## ⏱️ Estimation temps

| Contenu | Quantité | Temps estimé |
|---------|----------|--------------|
| Homepage | 28 textes | ~5 minutes |
| Authors | 56 textes | ~15 minutes |
| **Total** | **84 textes** | **~20 minutes** |

(Avec rate limiting de 1 seconde entre chaque appel API)
