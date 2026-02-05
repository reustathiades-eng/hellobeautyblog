# PROGRESS.md — État d'avancement du projet
> Dernière mise à jour : 5 février 2026 — 15h30

## ✅ TERMINÉ

### Infrastructure — Serveur de développement (olfapedia)
- [x] Hugo + config multilingue sur olfapedia:/home/ubuntu/hbb
- [x] 14 langues configurées avec slugs traduits
- [x] Thème hellobeauty (Fresh & Modern, rose poudré)
- [x] Domain hellobeautyblog.com actif
- [x] GitHub repo (reustathiades-eng/hellobeautyblog) — sert de backup

### Infrastructure — VPS Production (ovh-vps : 54.36.208.49)
- [x] VPS OVH Ubuntu 24.04 (6 vCores, 12 Go RAM, 100 Go SSD)
- [x] Docker + Docker Compose installés
- [x] n8n + PostgreSQL running (docker containers)
- [x] Hugo Extended 0.142.0 installé
- [x] Nginx configuré (site principal + n8n reverse proxy)
- [x] SSL site principal (certificat auto-signé + Cloudflare Full)
- [x] SSL n8n via Let's Encrypt (valide jusqu'au 6 mai 2026)
- [x] DNS Cloudflare : hellobeautyblog.com (proxied), n8n.hellobeautyblog.com (DNS only)
- [x] Firewall UFW activé (SSH, 80, 443)
- [x] Fail2ban installé et actif
- [x] Webhook auto-deploy (GitHub push → git pull → Hugo build)
- [x] Site live : https://hellobeautyblog.com ✅
- [x] n8n live : https://n8n.hellobeautyblog.com ✅
- [x] Scripts utilitaires : build.sh, deploy.sh, purge-cache.sh, webhook.sh
- [x] Cron maintenance : certbot renew, docker prune, log rotation
- [x] Swap 2 Go ajouté sur olfapedia (éviter OOM MariaDB/Redis)

### n8n — Automatisation
- [x] Compte owner créé (Romain)
- [x] Licence gratuite activée
- [x] Clé API Claude injectée dans l'environnement Docker (ANTHROPIC_API_KEY)
- [x] Volume /var/www/hellobeautyblog monté dans le container n8n
- [x] Workflow "HelloBeauty — Publication Quotidienne" importé
  - Cron 10h00 ou Test Manuel → Lire next_batch.json → Loop produits → Claude API → Formater Markdown → Écrire fichier → Hugo Build → Git Push
- [x] Fichier test next_batch.json créé (1 produit Chanel Chance Eau Tendre)

### Veille Nouveautés Sephora FR
- [x] Script `veille/sephora_watch.py` opérationnel sur olfapedia
- [x] Scrape les pages Nouveautés Sephora FR via API Demandware (AJAX)
- [x] 5 catégories Nouveautés : NC301 (parfum), NC302 (maquillage), NC303 (soin visage), NC304 (corps & bain), NC307 (cheveux)
- [x] Filtre par marques connues HBB, exclut coffrets/combos/outils
- [x] Classification par catégorie source (pas par breadcrumb)
- [x] Tracking PIDs pour ne détecter que les vrais ajouts
- [x] Premier run : 438 produits scannés → 163 matchent nos marques → 128 nouveautés identifiées
- [x] Résultats : `veille/results/veille_YYYY-MM-DD.json` + `veille/latest_new_products.json`
- [x] PIDs mémorisés : `veille/known_sephora_pids.json` (427 PIDs)

### Sous-catégories (199 × 14 langues = 2786 pages)
- [x] Perfumes : 52 sous-catégories
- [x] Skincare : 51 sous-catégories
- [x] Makeup : 51 sous-catégories
- [x] Haircare : 46 sous-catégories
- [x] Toutes les sous-catégories ont des URLs traduites dans les 14 langues
- [x] Contenu SEO généré via API Claude

### Traductions
- [x] 1911 titres/descriptions sous-catégories traduits
- [x] 1085 slugs d'URL traduits
- [x] JSONs data/categories/ synchronisés

### Contenu existant (59 articles)
- [x] 13 parfums complets (14 langues = 182 pages)
- [x] 11 articles skincare EN
- [x] 30 articles makeup EN
- [x] 5 articles haircare EN
- [x] 4 bios auteurs (14 langues = 56 pages)
- [x] 58 images parfums

### Listes de produits
- [x] 1 629 produits listés (brand, name, slug, subcategories)
- [x] Fichiers : generation/product_lists/{perfumes,skincare,makeup,haircare,gaps}.json
- ⚠️ **Les marques skincare/makeup/haircare n'ont pas été filtrées** — listes initiales larges, à affiner

---

## 🟡 EN COURS / PROCHAINE ÉTAPE

### Définir les marques acceptées par catégorie
- [x] Parfums : 100 marques définies (328 marques total cross-catégories)
- [ ] **Maquillage** : lister les marques acceptées pour HBB
- [ ] **Skincare** : lister les marques acceptées pour HBB
- [ ] **Haircare** : lister les marques acceptées pour HBB
- [ ] Mettre à jour les product_lists en conséquence
- [ ] Mettre à jour le script de veille pour filtrer par catégorie

### Tester le workflow n8n
- [ ] Exécuter le workflow avec le produit test (Chanel Chance Eau Tendre)
- [ ] Vérifier la fiche générée sur le site
- [ ] Ajuster le prompt/format si nécessaire

### Automatiser la veille Sephora
- [ ] Cron quotidien sur olfapedia (ou intégrer dans n8n)
- [ ] Bridge veille → next_batch.json (alimenter le workflow de publication)
- [ ] Notification des nouveautés détectées

---

## ⏳ À FAIRE (après workflow fonctionnel)

### Enrichir le workflow n8n
- [ ] Traduction en 13 langues (actuellement EN seulement)
- [ ] Gestion d'images (téléchargement + placement)
- [ ] Purge cache Cloudflare (remplir .env.cloudflare : CF_ZONE_ID + CF_API_TOKEN)
- [ ] Notification email/Slack en fin de process
- [ ] Sélection automatique du batch quotidien

### Production de contenu
- [ ] Générer les ~1 570 produits restants via n8n (30/jour × 14 langues)

### Monétisation
- [ ] Intégrer Skimlinks
- [ ] Configurer Amazon Associates (multi-pays via OneLink)
- [ ] Intégrer Awin (Sephora, Douglas, Notino)
- [ ] Pages légales (mentions légales, CGU, affiliate disclosure)

### Technique
- [ ] Analytics (Plausible déjà dans le code, à vérifier)
- [ ] Sitemap optimization
- [ ] Performance audit (Core Web Vitals)

---

## 📊 ARCHITECTURE ACTUELLE

### Flux de publication
```
n8n (VPS) → Claude API → Fichiers .md → Hugo build → Site live
                                              ↓
                                    Git push (backup GitHub)
```

### Flux de veille nouveautés
```
Veille Sephora (olfapedia, quotidien)
  → Fetch 5 pages Nouveautés Sephora FR (NC301-NC307)
  → Filtrer par marques HBB + exclure coffrets/combos
  → Comparer PIDs connus → Identifier vrais ajouts
  → Sauvegarder résultats JSON
  → (à faire) Alimenter next_batch.json → n8n workflow
```

### Serveurs
| Serveur | Rôle | Accès MCP |
|---------|------|-----------|
| olfapedia | Dev Hugo + source + veille | olfapedia:exec |
| ovh-vps (54.36.208.49) | Production site + n8n | ovh-vps:exec |

### Produits à générer
| Catégorie | Total | Existants | Restants |
|-----------|-------|-----------|----------|
| Perfumes | 511 | 13 | 498 |
| Skincare | 278 | 11 | 267 |
| Makeup | 500 | 30 | 470 |
| Haircare | 270 | 5 | 265 |
| Gaps | 70 | 0 | 70 |
| **TOTAL** | **1 629** | **59** | **1 570** |
