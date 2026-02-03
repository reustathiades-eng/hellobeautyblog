#!/usr/bin/env python3
"""Duplicate EN subcategories to 13 other languages"""
import os, re, shutil

os.chdir("/home/ubuntu/hbb")

# Section slugs par langue
SECTIONS = {
    "skincare": {
        "en":"skincare","fr":"soins","de":"hautpflege","es":"cuidado-piel",
        "it":"skincare","pt":"cuidados-pele","nl":"huidverzorging","pl":"pielegnacja",
        "tr":"cilt-bakimi","ja":"skincare","ko":"skincare","zh":"skincare","ar":"skincare","hi":"skincare"
    },
    "makeup": {
        "en":"makeup","fr":"maquillage","de":"make-up","es":"maquillaje",
        "it":"trucco","pt":"maquiagem","nl":"make-up","pl":"makijaz",
        "tr":"makyaj","ja":"makeup","ko":"makeup","zh":"makeup","ar":"makeup","hi":"makeup"
    },
    "haircare": {
        "en":"haircare","fr":"cheveux","de":"haarpflege","es":"cabello",
        "it":"capelli","pt":"cabelos","nl":"haarverzorging","pl":"wlosy",
        "tr":"sac-bakimi","ja":"haircare","ko":"haircare","zh":"haircare","ar":"haircare","hi":"haircare"
    }
}

LANGS = ["fr","de","es","it","pt","nl","pl","tr","ja","ko","zh","ar","hi"]

created = 0
for section, section_slugs in SECTIONS.items():
    en_section = section_slugs["en"]
    en_base = f"content/en/{en_section}"
    
    # Liste des sous-dossiers EN
    if not os.path.isdir(en_base):
        continue
    
    for subcat in os.listdir(en_base):
        subcat_path = os.path.join(en_base, subcat)
        if not os.path.isdir(subcat_path):
            continue
        
        index_en = os.path.join(subcat_path, "_index.md")
        if not os.path.isfile(index_en):
            continue
        
        content_en = open(index_en, encoding="utf-8").read()
        
        # Extraire translationKey
        tk_match = re.search(r'translationKey:\s*"([^"]+)"', content_en)
        if not tk_match:
            print(f"SKIP {index_en}: no translationKey")
            continue
        tk = tk_match.group(1)
        
        for lang in LANGS:
            lang_section = section_slugs[lang]
            target_dir = f"content/{lang}/{lang_section}/{subcat}"
            target_file = os.path.join(target_dir, "_index.md")
            
            if os.path.exists(target_file):
                continue
            
            os.makedirs(target_dir, exist_ok=True)
            
            # Copier et adapter le contenu
            content_lang = content_en
            # Changer l'URL
            content_lang = re.sub(
                r'url:\s*"/en/[^"]+/"',
                f'url: "/{lang}/{lang_section}/{subcat}/"',
                content_lang
            )
            
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content_lang)
            
            created += 1

print(f"Created {created} files")
