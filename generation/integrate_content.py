#!/usr/bin/env python3
"""
HelloBeautyBlog - Content Integration Script
Integrates generated content into Hugo templates and markdown files
"""

import json
import re
from pathlib import Path

BASE_PATH = Path("/home/ubuntu/hbb")

LANGUAGES = ["en", "fr", "de", "es", "it", "pt", "nl", "pl", "tr", "ja", "ko", "zh", "ar", "hi"]

def integrate_homepage_content():
    """Integrate homepage SEO texts into index.html template"""
    
    # Load generated content
    content_file = BASE_PATH / "generation" / "homepage_content.json"
    if not content_file.exists():
        print("❌ homepage_content.json not found. Run generate_content.py first.")
        return
    
    with open(content_file, "r", encoding="utf-8") as f:
        content = json.load(f)
    
    # Read current index.html
    index_file = BASE_PATH / "themes" / "hellobeauty" / "layouts" / "index.html"
    index_html = index_file.read_text(encoding="utf-8")
    
    # Generate Hugo template code for intro texts
    intro_code = '{{ if eq $lang "en" }}' + content["intro"].get("en", "") 
    for lang in LANGUAGES[1:]:
        if lang in content["intro"]:
            intro_code += f'\n                {{ else if eq $lang "{lang}" }}' + content["intro"][lang]
    intro_code += '\n                {{ end }}'
    
    # Generate Hugo template code for bottom texts
    bottom_code = '{{ if eq $lang "en" }}' + content["bottom"].get("en", "")
    for lang in LANGUAGES[1:]:
        if lang in content["bottom"]:
            bottom_code += f'\n            {{ else if eq $lang "{lang}" }}' + content["bottom"][lang]
    bottom_code += '\n            {{ end }}'
    
    # Replace placeholders
    index_html = index_html.replace("[SEO_INTRO_TEXT]", intro_code)
    index_html = index_html.replace("[SEO_BOTTOM_TEXT]", bottom_code)
    
    # Write updated file
    index_file.write_text(index_html, encoding="utf-8")
    print("✅ Homepage index.html updated with SEO content")

def integrate_author_bios():
    """Integrate author bios into markdown files"""
    
    # Load generated content
    bios_file = BASE_PATH / "generation" / "author_bios.json"
    if not bios_file.exists():
        print("❌ author_bios.json not found. Run generate_content.py first.")
        return
    
    with open(bios_file, "r", encoding="utf-8") as f:
        bios = json.load(f)
    
    authors = ["sophie-laurent", "emma-chen", "isabella-romano", "olivia-taylor"]
    
    for author in authors:
        if author not in bios:
            print(f"⚠ No bios found for {author}")
            continue
            
        for lang in LANGUAGES:
            if lang not in bios[author]:
                print(f"⚠ No {lang} bio for {author}")
                continue
            
            # Path to author file
            author_file = BASE_PATH / "content" / lang / "authors" / f"{author}.md"
            
            if not author_file.exists():
                # Create directory and file
                author_file.parent.mkdir(parents=True, exist_ok=True)
                create_author_file(author, lang, bios[author][lang])
                print(f"✓ Created {author_file}")
            else:
                # Update existing file
                content = author_file.read_text(encoding="utf-8")
                
                # Find and replace placeholder
                placeholder_pattern = r'\[SEO_BIO_[A-Z_]+\]'
                if re.search(placeholder_pattern, content):
                    content = re.sub(placeholder_pattern, bios[author][lang], content)
                    author_file.write_text(content, encoding="utf-8")
                    print(f"✓ Updated {author_file}")
                else:
                    # Replace everything after the last ---
                    parts = content.split("---")
                    if len(parts) >= 3:
                        # Keep frontmatter, replace body
                        new_content = "---" + parts[1] + "---\n\n" + bios[author][lang]
                        author_file.write_text(new_content, encoding="utf-8")
                        print(f"✓ Replaced content in {author_file}")

def create_author_file(author: str, lang: str, bio: str):
    """Create a new author markdown file"""
    
    # Author metadata
    authors_meta = {
        "sophie-laurent": {
            "en": {"role": "Perfume Expert", "tagline": "Certified nose with 12 years of experience in the luxury perfume industry in Paris and Grasse."},
            "fr": {"role": "Experte Parfums", "tagline": "Nez certifiée avec 12 ans d'expérience dans l'industrie de la parfumerie de luxe à Paris et Grasse."},
            "de": {"role": "Parfüm-Expertin", "tagline": "Zertifizierte Nase mit 12 Jahren Erfahrung in der Luxusparfümindustrie in Paris und Grasse."},
            "es": {"role": "Experta en Perfumes", "tagline": "Nariz certificada con 12 años de experiencia en la industria del perfume de lujo en París y Grasse."},
            "it": {"role": "Esperta di Profumi", "tagline": "Naso certificato con 12 anni di esperienza nell'industria della profumeria di lusso a Parigi e Grasse."},
            "pt": {"role": "Especialista em Perfumes", "tagline": "Nariz certificada com 12 anos de experiência na indústria de perfumaria de luxo em Paris e Grasse."},
            "nl": {"role": "Parfum Expert", "tagline": "Gecertificeerde neus met 12 jaar ervaring in de luxe parfumindustrie in Parijs en Grasse."},
            "pl": {"role": "Ekspert Perfum", "tagline": "Certyfikowany nos z 12-letnim doświadczeniem w branży luksusowych perfum w Paryżu i Grasse."},
            "tr": {"role": "Parfüm Uzmanı", "tagline": "Paris ve Grasse'da lüks parfüm endüstrisinde 12 yıllık deneyime sahip sertifikalı burun."},
            "ja": {"role": "香水エキスパート", "tagline": "パリとグラースの高級香水業界で12年の経験を持つ認定調香師。"},
            "ko": {"role": "향수 전문가", "tagline": "파리와 그라스의 럭셔리 향수 산업에서 12년 경력의 공인 조향사."},
            "zh": {"role": "香水专家", "tagline": "在巴黎和格拉斯奢侈香水行业拥有12年经验的认证调香师。"},
            "ar": {"role": "خبيرة العطور", "tagline": "أنف معتمدة مع 12 عامًا من الخبرة في صناعة العطور الفاخرة في باريس وغراس."},
            "hi": {"role": "परफ्यूम विशेषज्ञ", "tagline": "पेरिस और ग्रास में लक्जरी परफ्यूम उद्योग में 12 साल के अनुभव के साथ प्रमाणित नाक।"},
        },
        # Add other authors similarly...
    }
    
    # Default fallback
    meta = authors_meta.get(author, {}).get(lang, authors_meta.get(author, {}).get("en", {"role": "Expert", "tagline": "Beauty expert"}))
    
    content = f"""---
title: "{author.replace('-', ' ').title()}"
role: "{meta['role']}"
tagline: "{meta['tagline']}"
image: "/images/authors/{author}.webp"
author_slug: "{author}"
---

{bio}
"""
    
    file_path = BASE_PATH / "content" / lang / "authors" / f"{author}.md"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("HelloBeautyBlog Content Integration")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python integrate_content.py homepage  - Integrate homepage content")
        print("  python integrate_content.py authors   - Integrate author bios")
        print("  python integrate_content.py all       - Integrate everything")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command in ["homepage", "all"]:
        print("\n📄 Integrating homepage content...")
        integrate_homepage_content()
    
    if command in ["authors", "all"]:
        print("\n👤 Integrating author bios...")
        integrate_author_bios()
    
    print("\n✅ Integration complete!")
