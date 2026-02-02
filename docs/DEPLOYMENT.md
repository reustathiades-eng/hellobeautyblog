# DEPLOYMENT.md — Déploiement et workflow Git
> Dernière mise à jour : 2 février 2026

## GitHub

| Élément | Valeur |
|---------|--------|
| Compte | reustathiades-eng |
| Repo | hellobeautyblog |
| URL | https://github.com/reustathiades-eng/hellobeautyblog |
| Branche | main |

## Cloudflare Pages

| Élément | Valeur |
|---------|--------|
| Projet | hellobeautyblog |
| Build command | `hugo --minify` |
| Output dir | `public` |
| Variable | `HUGO_VERSION = 0.121.0` |
| Domaine | hellobeautyblog.com |
| Auto-deploy | Oui, sur push main (~2 min) |

## Workflow standard

```bash
cd /home/ubuntu/hbb

# 1. Modifications
nano content/en/perfumes/nouveau.md
# ou lancer un script de génération

# 2. Vérifier localement (optionnel)
hugo server --bind 0.0.0.0

# 3. Déployer
git add .
git commit -m "feat: description claire"
git push origin main

# 4. Attendre ~2 min pour le build Cloudflare
```

## Conventions de commit

```
feat: Nouvelle fonctionnalité ou contenu
fix: Correction de bug
seo: Ajout/modification contenu SEO
style: Changement CSS/design
docs: Documentation
chore: Maintenance, nettoyage
```

## Commande rapide via generation

```bash
cd /home/ubuntu/hbb/generation
./run.sh deploy    # Fait git add + commit + push automatiquement
```

## Vérification post-déploiement

1. Attendre ~2 min après le push
2. Vérifier https://hellobeautyblog.com
3. Tester quelques pages dans différentes langues
4. Vérifier le dashboard Cloudflare si besoin

## Rollback

```bash
git log --oneline -10          # Voir les derniers commits
git revert HEAD                # Annuler le dernier commit
git push origin main           # Redéployer la version précédente
```
