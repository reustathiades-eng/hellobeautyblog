#!/bin/bash
# =============================================================
# validate_translations.sh — Vérifie les règles de traduction
# Lancer : bash scripts/validate_translations.sh
# =============================================================
cd /home/ubuntu/hbb
ERRORS=0
WARNINGS=0

echo "========================================"
echo "  VALIDATION TRANSLATIONS"
echo "========================================"

# 1. Fichiers _index.md SANS translationKey
echo -e "\n--- 1. _index.md sans translationKey ---"
while IFS= read -r f; do
  if ! grep -q "translationKey" "$f"; then
    echo "❌ $f"
    ((ERRORS++))
  fi
done < <(find content/en content/fr content/de content/es content/it content/pt content/nl content/pl content/tr content/ja content/ko content/zh content/ar content/hi -name "_index.md")

# 2. Produits parfum SANS translationKey
echo -e "\n--- 2. Produits parfum sans translationKey ---"
while IFS= read -r f; do
  [ "$(basename $f)" = "_index.md" ] && continue
  if ! grep -q "translationKey" "$f"; then
    echo "❌ $f"
    ((ERRORS++))
  fi
done < <(find content/en/perfumes/ -name "*.md" 2>/dev/null)

# 3. Articles traduits SANS translationKey
echo -e "\n--- 3. Articles sans translationKey ---"
for section in skincare makeup haircare blog; do
  while IFS= read -r f; do
    [ "$(basename $f)" = "_index.md" ] && continue
    if ! grep -q "translationKey" "$f"; then
      echo "❌ $f"
      ((ERRORS++))
    fi
  done < <(find content/en/$section/ -name "*.md" 2>/dev/null)
done

# 4. translationKey orphelins (EN a la clé mais pas toutes les langues)
echo -e "\n--- 4. translationKey EN sans correspondance dans autres langues ---"
LANGS=(fr de es it pt nl pl tr ja ko zh ar hi)
for f in content/en/perfumes/*.md; do
  [ "$(basename $f)" = "_index.md" ] && continue
  key=$(grep "translationKey:" "$f" | head -1 | sed 's/.*: *"//;s/".*//')
  [ -z "$key" ] && continue
  missing=""
  for lang in "${LANGS[@]}"; do
    found=$(grep -rl "translationKey: \"$key\"" content/$lang/ 2>/dev/null)
    [ -z "$found" ] && missing="$missing $lang"
  done
  if [ -n "$missing" ]; then
    echo "⚠️  $key manque dans:$missing"
    ((WARNINGS++))
  fi
done

# 5. translationKey dupliqués dans une même langue
echo -e "\n--- 5. translationKey dupliqués ---"
for lang in en fr de es it pt nl pl tr ja ko zh ar hi; do
  dupes=$(grep -rh "translationKey:" content/$lang/ 2>/dev/null | sed 's/.*: *"//;s/".*//' | sort | uniq -d)
  if [ -n "$dupes" ]; then
    echo "❌ $lang a des doublons: $dupes"
    ((ERRORS++))
  fi
done

# RÉSUMÉ
echo -e "\n========================================"
echo "  RÉSULTAT: $ERRORS erreurs, $WARNINGS warnings"
echo "========================================"
[ $ERRORS -eq 0 ] && echo "✅ Pas d'erreur critique" || echo "❌ $ERRORS erreurs à corriger"
[ $WARNINGS -gt 0 ] && echo "⚠️  $WARNINGS traductions manquantes"
