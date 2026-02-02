# LANGUAGES.md — Configuration multilingue
> Dernière mise à jour : 2 février 2026

## 14 langues configurées

| Code | Langue | Weight | Dossier content | Slug perfumes | Slug skincare | Slug makeup | Slug haircare |
|------|--------|--------|-----------------|---------------|---------------|-------------|---------------|
| en | English | 1 | content/en | perfumes | skincare | makeup | haircare |
| fr | Français | 2 | content/fr | parfums | soins | maquillage | cheveux |
| de | Deutsch | 3 | content/de | parfum | hautpflege | make-up | haarpflege |
| es | Español | 4 | content/es | perfumes | cuidado-piel | maquillaje | cabello |
| it | Italiano | 5 | content/it | profumi | skincare | trucco | capelli |
| pt | Português | 6 | content/pt | perfumes | skincare | maquiagem | cabelos |
| nl | Nederlands | 7 | content/nl | parfum | huidverzorging | make-up | haarverzorging |
| pl | Polski | 8 | content/pl | perfumy | pielegnacja | makijaz | wlosy |
| tr | Türkçe | 9 | content/tr | parfum | cilt-bakimi | makyaj | sac-bakimi |
| ja | 日本語 | 10 | content/ja | perfumes | skincare | makeup | haircare |
| ko | 한국어 | 11 | content/ko | perfumes | skincare | makeup | haircare |
| zh | 中文 | 12 | content/zh | perfumes | skincare | makeup | haircare |
| ar | العربية | 13 | content/ar | perfumes | skincare | makeup | haircare |
| hi | हिन्दी | 14 | content/hi | perfumes | skincare | makeup | haircare |

## Règles importantes

1. **Slugs traduits** : FR, DE, ES, IT, PT, NL, PL, TR ont des slugs localisés. JA, KO, ZH, AR, HI utilisent les slugs EN.
2. **RTL** : Seul AR a `rtl: true` dans params.
3. **Dossiers content** : Le nom du dossier DOIT correspondre au slug de la langue (ex: `content/fr/parfums/` et non `content/fr/perfumes/`).
4. **_index.md** : Chaque dossier section doit avoir un `_index.md` avec title et description traduits.
5. **translationKey** : Chaque produit a un `translationKey` identique dans toutes les langues (ex: `translationKey: "black-opium"`).

## Structure URL résultante

```
https://hellobeautyblog.com/en/perfumes/black-opium/
https://hellobeautyblog.com/fr/parfums/black-opium/
https://hellobeautyblog.com/de/parfum/black-opium/
https://hellobeautyblog.com/it/profumi/black-opium/
```

## Contenu par langue (état au 2 février 2026)

| Langue | Perfumes | Skincare | Makeup | Haircare | Blog | Authors |
|--------|----------|----------|--------|----------|------|---------|
| en | 13 | 11 | 30 | 5 | 15 | 4 |
| fr | 13 | 5 | 3 | 1 | 0 | 4 |
| de | 13 | 5 | 3 | 1 | 0 | 4 |
| es | 13 | 5 | 3 | 1 | 0 | 4 |
| it | 12 | 5 | 3 | 1 | 0 | 4 |
| pt | 13 | 5 | 3 | 1 | 0 | 4 |
| nl | 12 | 5 | 3 | 1 | 0 | 4 |
| pl | 12 | 5 | 3 | 1 | 0 | 4 |
| tr | 13 | 5 | 3 | 1 | 0 | 4 |
| ar | 13 | 5 | 3 | 1 | 0 | 4 |
| zh | 13 | 5 | 3 | 1 | 0 | 4 |
| ja | 13 | 5 | 3 | 1 | 0 | 4 |
| ko | 13 | 5 | 3 | 1 | 0 | 4 |
| hi | 13 | 5 | 3 | 1 | 0 | 4 |

> Note : EN a le plus de contenu car c'est la base migrée. Les autres langues ont les parfums complets + une sélection d'articles.

## Fichier de référence

La config complète est dans : `config/_default/languages.yaml`
