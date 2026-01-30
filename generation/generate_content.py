#!/usr/bin/env python3
"""
HelloBeautyBlog - Content Generation Script
Generates homepage SEO texts and author bios in 14 languages via Claude API
"""

import anthropic
import os
import json
import time
from pathlib import Path

# Configuration
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
MODEL = "claude-sonnet-4-20250514"
BASE_PATH = Path("/home/ubuntu/hbb")

# 14 languages configuration
LANGUAGES = {
    "en": {"name": "English", "native": "English"},
    "fr": {"name": "French", "native": "Français"},
    "de": {"name": "German", "native": "Deutsch"},
    "es": {"name": "Spanish", "native": "Español"},
    "it": {"name": "Italian", "native": "Italiano"},
    "pt": {"name": "Portuguese", "native": "Português"},
    "nl": {"name": "Dutch", "native": "Nederlands"},
    "pl": {"name": "Polish", "native": "Polski"},
    "tr": {"name": "Turkish", "native": "Türkçe"},
    "ja": {"name": "Japanese", "native": "日本語"},
    "ko": {"name": "Korean", "native": "한국어"},
    "zh": {"name": "Chinese", "native": "中文"},
    "ar": {"name": "Arabic", "native": "العربية"},
    "hi": {"name": "Hindi", "native": "हिन्दी"},
}

# Authors data
AUTHORS = {
    "sophie-laurent": {
        "name": "Sophie Laurent",
        "role_en": "Perfume Expert",
        "role_fr": "Experte Parfums",
        "nationality": "French",
        "city": "Paris/Grasse",
        "years": 12,
        "specialty": "luxury perfumery, niche fragrances, olfactory analysis",
        "background": "Certified nose (ISIPCA Versailles), former evaluator at Givaudan, Master's in Fragrance Chemistry from Grasse Institute",
        "personality": "Sophisticated, passionate about raw materials, loves vintage perfumes, speaks poetically about scent"
    },
    "emma-chen": {
        "name": "Emma Chen",
        "role_en": "Skincare Specialist",
        "role_fr": "Spécialiste Skincare",
        "nationality": "Korean-American",
        "city": "Seoul/New York",
        "years": 10,
        "specialty": "K-beauty, J-beauty, active ingredients, sensitive skin, skin barrier",
        "background": "MD in Dermatology from Seoul National University, former R&D consultant at Amorepacific, CIDESCO certified",
        "personality": "Scientific yet approachable, obsessed with ingredient lists, believes in gentle routines"
    },
    "isabella-romano": {
        "name": "Isabella Romano",
        "role_en": "Professional Makeup Artist",
        "role_fr": "Maquilleuse Professionnelle",
        "nationality": "Italian",
        "city": "Milan",
        "years": 15,
        "specialty": "editorial makeup, runway looks, bridal beauty, color theory",
        "background": "Lead artist at Milan Fashion Week, worked with Vogue Italia and Elle, trained at Accademia del Lusso",
        "personality": "Creative and bold, loves experimenting with color, advocates for inclusive beauty"
    },
    "olivia-taylor": {
        "name": "Olivia Taylor",
        "role_en": "Haircare Expert",
        "role_fr": "Experte Capillaire",
        "nationality": "British",
        "city": "London",
        "years": 11,
        "specialty": "scalp health, natural haircare, curly hair methods, trichology",
        "background": "IAT Certified Trichologist, Vidal Sassoon Academy graduate, consultant for Olaplex, author of 'The Scalp Solution'",
        "personality": "Warm and nurturing, believes healthy hair starts at the scalp, passionate about clean formulations"
    }
}

client = anthropic.Anthropic(api_key=API_KEY)

def generate_content(prompt: str, max_tokens: int = 2000) -> str:
    """Call Claude API to generate content"""
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error: {e}")
        return None

# ============================================================================
# HOMEPAGE SEO CONTENT BRIEFS
# ============================================================================

def get_homepage_intro_prompt(lang_code: str, lang_name: str) -> str:
    """Brief for homepage intro SEO text"""
    return f"""You are a professional beauty copywriter for HelloBeautyBlog.com, a premium multilingual beauty blog.

Write a SHORT introductory paragraph (2-3 sentences, max 50 words) for the homepage in {lang_name}.

BRAND VOICE:
- Warm, welcoming, expertise without arrogance
- Modern luxury aesthetic (think rose powder pink, elegant)
- Independent and honest - we're not paid by brands
- Passionate about helping readers find their perfect products

CONTENT REQUIREMENTS:
- Welcome visitors to the blog
- Mention we cover perfumes, skincare, makeup, and haircare
- Emphasize expert reviews and honest recommendations
- Create a sense of discovery and beauty journey

LANGUAGE: Write ONLY in {lang_name}. Native quality, not translated.
FORMAT: Return ONLY the paragraph text, no quotes, no labels, no explanation.

Example tone (DO NOT COPY, just for reference):
"Welcome to your trusted destination for beauty discoveries. Our team of experts shares honest reviews and personalized recommendations across perfumes, skincare, makeup and haircare to help you find products that truly work for you."
"""

def get_homepage_bottom_prompt(lang_code: str, lang_name: str) -> str:
    """Brief for homepage bottom SEO text"""
    return f"""You are a professional beauty copywriter and SEO expert for HelloBeautyBlog.com.

Write a comprehensive "About" section (200-250 words) for the bottom of the homepage in {lang_name}.

BRAND IDENTITY:
- HelloBeautyBlog is an independent beauty blog (not affiliated with any brand)
- Team of 4 experts: perfume specialist, skincare dermatologist, makeup artist, haircare trichologist
- Available in 14 languages to serve a global audience
- Focus on honest, in-depth reviews based on real testing
- Modern luxury aesthetic with a welcoming, inclusive approach

SEO KEYWORDS TO NATURALLY INCLUDE:
- beauty blog, perfume reviews, skincare advice, makeup tips, haircare guide
- honest reviews, expert recommendations, independent beauty
- luxury beauty, best perfumes, skincare routine, makeup tutorials

CONTENT STRUCTURE:
1. Opening: What HelloBeautyBlog is and our mission (2-3 sentences)
2. Our expertise: Brief mention of our specialist team (2-3 sentences)
3. What we offer: Types of content - reviews, guides, tips (2-3 sentences)
4. Our values: Independence, honesty, real testing (2-3 sentences)
5. Closing: Invitation to explore and discover (1-2 sentences)

LANGUAGE: Write ONLY in {lang_name}. Native quality, fluent, natural.
FORMAT: Return ONLY the text as flowing paragraphs. No headers, no bullet points, no labels.
"""

# ============================================================================
# AUTHOR BIO BRIEFS
# ============================================================================

def get_author_bio_prompt(author_key: str, lang_code: str, lang_name: str) -> str:
    """Brief for author detailed biography"""
    author = AUTHORS[author_key]
    
    return f"""You are writing a detailed professional biography for {author['name']}, {author['role_en']} at HelloBeautyBlog.com.

AUTHOR PROFILE:
- Name: {author['name']}
- Role: {author['role_en']}
- Nationality: {author['nationality']}
- Based in: {author['city']}
- Years of experience: {author['years']}
- Specialties: {author['specialty']}
- Background: {author['background']}
- Personality: {author['personality']}

Write a compelling, personal biography (300-400 words) in {lang_name}.

STRUCTURE:
1. OPENING HOOK (2-3 sentences): Start with what drives their passion for beauty. Make it personal and engaging.

2. PROFESSIONAL JOURNEY (1 paragraph): Their career path, key achievements, where they trained/worked. Be specific with names and places.

3. EXPERTISE & PHILOSOPHY (1 paragraph): What makes their approach unique. Their professional philosophy. What they believe in.

4. AT HELLOBEAUTYBLOG (2-3 sentences): Their role on the blog, what type of content they create, what readers can expect from their articles.

5. PERSONAL TOUCH (2-3 sentences): A human detail - maybe a favorite product category, what they do when not writing, or a fun fact.

TONE:
- Professional but warm and approachable
- Third person ("Sophie believes..." not "I believe...")
- Confident expertise without arrogance
- Authentic and relatable

LANGUAGE: Write ONLY in {lang_name}. Native quality, culturally appropriate.
FORMAT: Return ONLY the biography as flowing paragraphs. No headers, no bullet points, no "Bio:" labels.
"""

# ============================================================================
# GENERATION FUNCTIONS
# ============================================================================

def generate_homepage_content():
    """Generate homepage SEO texts for all languages"""
    results = {"intro": {}, "bottom": {}}
    
    for lang_code, lang_info in LANGUAGES.items():
        print(f"\n📝 Generating homepage content for {lang_info['name']}...")
        
        # Intro text
        print(f"  → Intro text...")
        intro_prompt = get_homepage_intro_prompt(lang_code, lang_info['name'])
        intro_text = generate_content(intro_prompt, max_tokens=200)
        if intro_text:
            results["intro"][lang_code] = intro_text.strip()
            print(f"    ✓ Done ({len(intro_text)} chars)")
        
        time.sleep(1)  # Rate limiting
        
        # Bottom text
        print(f"  → Bottom SEO text...")
        bottom_prompt = get_homepage_bottom_prompt(lang_code, lang_info['name'])
        bottom_text = generate_content(bottom_prompt, max_tokens=800)
        if bottom_text:
            results["bottom"][lang_code] = bottom_text.strip()
            print(f"    ✓ Done ({len(bottom_text)} chars)")
        
        time.sleep(1)
    
    # Save results
    output_file = BASE_PATH / "generation" / "homepage_content.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Homepage content saved to {output_file}")
    
    return results

def generate_author_bios():
    """Generate author bios for all languages"""
    results = {}
    
    for author_key, author_info in AUTHORS.items():
        results[author_key] = {}
        print(f"\n👤 Generating bios for {author_info['name']}...")
        
        for lang_code, lang_info in LANGUAGES.items():
            print(f"  → {lang_info['name']}...")
            
            prompt = get_author_bio_prompt(author_key, lang_code, lang_info['name'])
            bio_text = generate_content(prompt, max_tokens=1200)
            
            if bio_text:
                results[author_key][lang_code] = bio_text.strip()
                print(f"    ✓ Done ({len(bio_text)} chars)")
            
            time.sleep(1)  # Rate limiting
    
    # Save results
    output_file = BASE_PATH / "generation" / "author_bios.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Author bios saved to {output_file}")
    
    return results

def update_author_files(bios: dict):
    """Update author markdown files with generated bios"""
    for author_key, lang_bios in bios.items():
        for lang_code, bio_text in lang_bios.items():
            file_path = BASE_PATH / "content" / lang_code / "authors" / f"{author_key}.md"
            
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                # Replace placeholder with actual bio
                placeholder = f"[SEO_BIO_{author_key.upper().replace('-', '_')}]"
                if lang_code == "fr":
                    placeholder = f"[SEO_BIO_{author_key.upper().replace('-', '_')}_FR]"
                
                if placeholder in content:
                    content = content.replace(placeholder, bio_text)
                    file_path.write_text(content, encoding="utf-8")
                    print(f"✓ Updated {file_path}")
            else:
                # Create the file if it doesn't exist
                print(f"⚠ File not found: {file_path} - will need to create")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("HelloBeautyBlog Content Generator")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python generate_content.py homepage   - Generate homepage SEO texts")
        print("  python generate_content.py authors    - Generate author bios")
        print("  python generate_content.py all        - Generate everything")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command in ["homepage", "all"]:
        print("\n" + "=" * 60)
        print("GENERATING HOMEPAGE CONTENT (14 languages × 2 sections)")
        print("=" * 60)
        generate_homepage_content()
    
    if command in ["authors", "all"]:
        print("\n" + "=" * 60)
        print("GENERATING AUTHOR BIOS (4 authors × 14 languages)")
        print("=" * 60)
        bios = generate_author_bios()
        
        print("\n" + "=" * 60)
        print("UPDATING AUTHOR FILES")
        print("=" * 60)
        update_author_files(bios)
    
    print("\n" + "=" * 60)
    print("✅ GENERATION COMPLETE!")
    print("=" * 60)
