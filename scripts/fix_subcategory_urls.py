#!/usr/bin/env python3
"""Replace slug with url in all subcategory _index.md files."""
import os, re

SECTION_DIRS = {
    "en": "perfumes", "fr": "parfums", "de": "parfum", "es": "perfumes",
    "it": "profumi", "pt": "perfumes", "nl": "parfum", "pl": "perfumy",
    "tr": "parfum", "ja": "perfumes", "ko": "perfumes", "zh": "perfumes",
    "ar": "perfumes", "hi": "perfumes"
}

# Section slug in URL (may differ from folder name)
SECTION_URL_SLUGS = {
    "en": "perfumes", "fr": "parfums", "de": "parfum", "es": "perfumes",
    "it": "profumi", "pt": "perfumes", "nl": "parfum", "pl": "perfumy",
    "tr": "parfum", "ja": "perfumes", "ko": "perfumes", "zh": "perfumes",
    "ar": "perfumes", "hi": "perfumes"
}

LATIN_LANGS = ["en","fr","de","es","it","pt","nl","pl","tr"]

SLUGS = {
  "women":{"fr":"femme","de":"damen","es":"mujer","it":"donna","pt":"feminino","nl":"dames","pl":"damskie","tr":"kadin"},
  "men":{"fr":"homme","de":"herren","es":"hombre","it":"uomo","pt":"masculino","nl":"heren","pl":"meskie","tr":"erkek"},
  "unisex":{"fr":"unisexe","de":"unisex","es":"unisex","it":"unisex","pt":"unissex","nl":"unisex","pl":"unisex","tr":"unisex"},
  "floral":{"fr":"floral","de":"blumig","es":"floral","it":"floreale","pt":"floral","nl":"bloemig","pl":"kwiatowe","tr":"ciceksi"},
  "oriental":{"fr":"oriental","de":"orientalisch","es":"oriental","it":"orientale","pt":"oriental","nl":"oosters","pl":"orientalne","tr":"oryantal"},
  "woody":{"fr":"boise","de":"holzig","es":"amaderado","it":"legnoso","pt":"amadeirado","nl":"houtachtig","pl":"drzewne","tr":"odunsu"},
  "fresh":{"fr":"frais","de":"frisch","es":"fresco","it":"fresco","pt":"fresco","nl":"fris","pl":"swieze","tr":"taze"},
  "aromatic":{"fr":"aromatique","de":"aromatisch","es":"aromatico","it":"aromatico","pt":"aromatico","nl":"aromatisch","pl":"aromatyczne","tr":"aromatik"},
  "chypre":{"fr":"chypre","de":"chypre","es":"chipre","it":"cipriato","pt":"chipre","nl":"chypre","pl":"chypre","tr":"chypre"},
  "gourmand":{"fr":"gourmand","de":"gourmand","es":"gourmand","it":"gourmand","pt":"gourmand","nl":"gourmand","pl":"gourmand","tr":"gurme"},
  "floral-fruity":{"fr":"floral-fruite","de":"blumig-fruchtig","es":"floral-afrutado","it":"floreale-fruttato","pt":"floral-frutado","nl":"bloemig-fruitig","pl":"kwiatowo-owocowe","tr":"ciceksi-meyveli"},
  "floral-white":{"fr":"floral-blanc","de":"weiss-blumig","es":"floral-blanco","it":"floreale-bianco","pt":"floral-branco","nl":"wit-bloemig","pl":"kwiatowo-biale","tr":"beyaz-ciceksi"},
  "floral-powdery":{"fr":"floral-poudre","de":"blumig-pudrig","es":"floral-empolvado","it":"floreale-cipriato","pt":"floral-aveludado","nl":"bloemig-poederig","pl":"kwiatowo-pudrowe","tr":"ciceksi-pudra"},
  "floral-green":{"fr":"floral-vert","de":"blumig-gruen","es":"floral-verde","it":"floreale-verde","pt":"floral-verde","nl":"bloemig-groen","pl":"kwiatowo-zielone","tr":"ciceksi-yesil"},
  "floral-aldehyde":{"fr":"floral-aldehyde","de":"blumig-aldehyd","es":"floral-aldehido","it":"floreale-aldeide","pt":"floral-aldeido","nl":"bloemig-aldehyde","pl":"kwiatowo-aldehydowe","tr":"ciceksi-aldehit"},
  "floral-aquatic":{"fr":"floral-aquatique","de":"blumig-aquatisch","es":"floral-acuatico","it":"floreale-acquatico","pt":"floral-aquatico","nl":"bloemig-aquatisch","pl":"kwiatowo-wodne","tr":"ciceksi-akuatik"},
  "oriental-spicy":{"fr":"oriental-epice","de":"orientalisch-wuerzig","es":"oriental-especiado","it":"orientale-speziato","pt":"oriental-picante","nl":"oosters-kruidig","pl":"orientalno-korzenne","tr":"oryantal-baharatli"},
  "oriental-vanilla":{"fr":"oriental-vanille","de":"orientalisch-vanille","es":"oriental-vainilla","it":"orientale-vaniglia","pt":"oriental-baunilha","nl":"oosters-vanille","pl":"orientalno-waniliowe","tr":"oryantal-vanilya"},
  "oriental-amber":{"fr":"oriental-ambre","de":"orientalisch-amber","es":"oriental-ambar","it":"orientale-ambra","pt":"oriental-ambar","nl":"oosters-amber","pl":"orientalno-ambrowe","tr":"oryantal-amber"},
  "oriental-woody":{"fr":"oriental-boise","de":"orientalisch-holzig","es":"oriental-amaderado","it":"orientale-legnoso","pt":"oriental-amadeirado","nl":"oosters-houtachtig","pl":"orientalno-drzewne","tr":"oryantal-odunsu"},
  "oriental-floral":{"fr":"oriental-floral","de":"orientalisch-blumig","es":"oriental-floral","it":"orientale-floreale","pt":"oriental-floral","nl":"oosters-bloemig","pl":"orientalno-kwiatowe","tr":"oryantal-ciceksi"},
  "woody-aromatic":{"fr":"boise-aromatique","de":"holzig-aromatisch","es":"amaderado-aromatico","it":"legnoso-aromatico","pt":"amadeirado-aromatico","nl":"houtachtig-aromatisch","pl":"drzewno-aromatyczne","tr":"odunsu-aromatik"},
  "woody-spicy":{"fr":"boise-epice","de":"holzig-wuerzig","es":"amaderado-especiado","it":"legnoso-speziato","pt":"amadeirado-picante","nl":"houtachtig-kruidig","pl":"drzewno-korzenne","tr":"odunsu-baharatli"},
  "woody-dry":{"fr":"boise-sec","de":"holzig-trocken","es":"amaderado-seco","it":"legnoso-secco","pt":"amadeirado-seco","nl":"houtachtig-droog","pl":"drzewno-suche","tr":"odunsu-kuru"},
  "woody-mossy":{"fr":"boise-moussu","de":"holzig-moosig","es":"amaderado-musgoso","it":"legnoso-muschioso","pt":"amadeirado-musgoso","nl":"houtachtig-mosachtig","pl":"drzewno-mszyste","tr":"odunsu-yosunlu"},
  "woody-earthy":{"fr":"boise-terreux","de":"holzig-erdig","es":"amaderado-terroso","it":"legnoso-terroso","pt":"amadeirado-terroso","nl":"houtachtig-aards","pl":"drzewno-ziemiste","tr":"odunsu-topraksi"},
  "fresh-citrus":{"fr":"agrumes","de":"zitrus","es":"citrico","it":"agrumato","pt":"citrico","nl":"citrus","pl":"cytrusowe","tr":"narenciye"},
  "fresh-aquatic":{"fr":"aquatique","de":"aquatisch","es":"acuatico","it":"acquatico","pt":"aquatico","nl":"aquatisch","pl":"wodne","tr":"akuatik"},
  "fresh-green":{"fr":"vert","de":"gruen","es":"verde","it":"verde","pt":"verde","nl":"groen","pl":"zielone","tr":"yesil"},
  "fresh-ozonic":{"fr":"ozonique","de":"ozonisch","es":"ozonico","it":"ozonico","pt":"ozonico","nl":"ozonisch","pl":"ozonowe","tr":"ozonik"},
  "fresh-fruity":{"fr":"frais-fruite","de":"frisch-fruchtig","es":"fresco-afrutado","it":"fresco-fruttato","pt":"fresco-frutado","nl":"fris-fruitig","pl":"swiezo-owocowe","tr":"taze-meyveli"},
  "aromatic-fougere":{"fr":"fougere","de":"fougere","es":"fougere","it":"fougere","pt":"fougere","nl":"fougere","pl":"fougere","tr":"fougere"},
  "aromatic-herbal":{"fr":"herbes","de":"krauter","es":"herbal","it":"erbaceo","pt":"herbal","nl":"kruidig","pl":"ziolowe","tr":"bitkisel"},
  "aromatic-spicy":{"fr":"aromatique-epice","de":"aromatisch-wuerzig","es":"aromatico-especiado","it":"aromatico-speziato","pt":"aromatico-picante","nl":"aromatisch-kruidig","pl":"aromatyczno-korzenne","tr":"aromatik-baharatli"},
  "aromatic-marine":{"fr":"marin","de":"marin","es":"marino","it":"marino","pt":"marinho","nl":"marien","pl":"morskie","tr":"deniz"},
  "chypre-fruity":{"fr":"chypre-fruite","de":"chypre-fruchtig","es":"chipre-afrutado","it":"cipriato-fruttato","pt":"chipre-frutado","nl":"chypre-fruitig","pl":"chypre-owocowe","tr":"chypre-meyveli"},
  "chypre-floral":{"fr":"chypre-floral","de":"chypre-blumig","es":"chipre-floral","it":"cipriato-floreale","pt":"chipre-floral","nl":"chypre-bloemig","pl":"chypre-kwiatowe","tr":"chypre-ciceksi"},
  "chypre-leather":{"fr":"chypre-cuire","de":"chypre-leder","es":"chipre-cuero","it":"cipriato-pelle","pt":"chipre-couro","nl":"chypre-leer","pl":"chypre-skorzane","tr":"chypre-deri"},
  "chypre-green":{"fr":"chypre-vert","de":"chypre-gruen","es":"chipre-verde","it":"cipriato-verde","pt":"chipre-verde","nl":"chypre-groen","pl":"chypre-zielone","tr":"chypre-yesil"},
  "gourmand-vanilla":{"fr":"gourmand-vanille","de":"gourmand-vanille","es":"gourmand-vainilla","it":"gourmand-vaniglia","pt":"gourmand-baunilha","nl":"gourmand-vanille","pl":"gourmand-waniliowe","tr":"gurme-vanilya"},
  "gourmand-sweet":{"fr":"sucre","de":"suess","es":"dulce","it":"dolce","pt":"doce","nl":"zoet","pl":"slodkie","tr":"tatli"},
  "gourmand-coffee":{"fr":"cafe","de":"kaffee","es":"cafe","it":"caffe","pt":"cafe","nl":"koffie","pl":"kawowe","tr":"kahve"},
  "gourmand-chocolate":{"fr":"chocolat","de":"schokolade","es":"chocolate","it":"cioccolato","pt":"chocolate","nl":"chocolade","pl":"czekoladowe","tr":"cikolata"},
  "everyday":{"fr":"quotidien","de":"alltag","es":"diario","it":"quotidiano","pt":"dia-a-dia","nl":"dagelijks","pl":"codzienny","tr":"gunluk"},
  "evening":{"fr":"soiree","de":"abend","es":"noche","it":"sera","pt":"noite","nl":"avond","pl":"wieczorowy","tr":"aksam"},
  "romantic":{"fr":"romantique","de":"romantisch","es":"romantico","it":"romantico","pt":"romantico","nl":"romantisch","pl":"romantyczne","tr":"romantik"},
  "office":{"fr":"bureau","de":"buero","es":"oficina","it":"ufficio","pt":"escritorio","nl":"kantoor","pl":"biurowe","tr":"ofis"},
  "summer":{"fr":"ete","de":"sommer","es":"verano","it":"estate","pt":"verao","nl":"zomer","pl":"letnie","tr":"yaz"},
  "winter":{"fr":"hiver","de":"winter","es":"invierno","it":"inverno","pt":"inverno","nl":"winter","pl":"zimowe","tr":"kis"},
  "wedding":{"fr":"mariage","de":"hochzeit","es":"boda","it":"matrimonio","pt":"casamento","nl":"bruiloft","pl":"slubne","tr":"dugun"},
  "sport":{"fr":"sport","de":"sport","es":"deporte","it":"sport","pt":"esporte","nl":"sport","pl":"sportowe","tr":"spor"},
  "travel":{"fr":"voyage","de":"reise","es":"viaje","it":"viaggio","pt":"viagem","nl":"reis","pl":"podrozne","tr":"seyahat"},
}

def get_slug(en_slug, lang):
    if lang == "en":
        return en_slug
    if lang not in LATIN_LANGS:
        return en_slug
    return SLUGS.get(en_slug, {}).get(lang, en_slug)

BASE = "/home/ubuntu/hbb/content"
total = 0

for lang in SECTION_DIRS:
    section_dir = SECTION_DIRS[lang]
    section_url = SECTION_URL_SLUGS[lang]
    perfume_dir = os.path.join(BASE, lang, section_dir)
    count = 0
    
    for folder in sorted(os.listdir(perfume_dir)):
        idx_path = os.path.join(perfume_dir, folder, "_index.md")
        if not os.path.isdir(os.path.join(perfume_dir, folder)) or not os.path.exists(idx_path):
            continue
        
        translated_slug = get_slug(folder, lang)
        full_url = f"/{lang}/{section_url}/{translated_slug}/"
        tkey = f"perfumes-{folder}"
        
        with open(idx_path, 'r') as f:
            content = f.read()
        
        # Remove old slug line, add url line
        lines = content.split('\n')
        new_lines = []
        has_url = False
        has_tkey = False
        
        for line in lines:
            if line.startswith('slug:'):
                continue  # Remove slug line
            if line.startswith('url:'):
                line = f'url: "{full_url}"'
                has_url = True
            if line.startswith('translationKey:'):
                has_tkey = True
            new_lines.append(line)
        
        # Insert url and translationKey before closing ---
        result = []
        closed = False
        first_dash = True
        for line in new_lines:
            if line.strip() == '---' and not first_dash and not closed:
                if not has_url:
                    result.append(f'url: "{full_url}"')
                if not has_tkey:
                    result.append(f'translationKey: "{tkey}"')
                closed = True
            if line.strip() == '---' and first_dash:
                first_dash = False
            result.append(line)
        
        with open(idx_path, 'w') as f:
            f.write('\n'.join(result))
        
        count += 1
    
    print(f"  {lang}: {count} files")
    total += count

print(f"\nTotal: {total} files updated with url frontmatter")
