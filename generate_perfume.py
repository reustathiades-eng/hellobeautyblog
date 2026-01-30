import anthropic
import json

client = anthropic.Anthropic()

def generate_perfume_review(perfume_data, language='en'):
    with open('/home/ubuntu/hbb/PERFUME_BRIEF.md', 'r') as f:
        brief = f.read()
    
    lang_names = {
        'en': 'English', 'fr': 'French', 'de': 'German', 'es': 'Spanish',
        'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'pl': 'Polish',
        'tr': 'Turkish', 'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese',
        'ar': 'Arabic', 'hi': 'Hindi'
    }
    
    prompt = f"""You are an expert perfume reviewer for HelloBeautyBlog.com. Generate a complete perfume review in {lang_names.get(language, 'English')} following the brief below.

BRIEF:
{brief}

PERFUME DATA:
{json.dumps(perfume_data, indent=2)}

Generate a complete Hugo markdown file with:
1. Full YAML front matter with all fields from the brief
2. Engaging, professional content (800-1200 words)
3. Personal experience and sensory descriptions
4. SEO-optimized but natural writing
5. Translate ALL fields including notes, seasons, occasions to {lang_names.get(language, 'English')}

Output ONLY the markdown file content, starting with --- for the front matter."""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

# Données Boss Alive
boss_alive = {
    "brand": "Hugo Boss",
    "productName": "Boss Alive",
    "concentration": "Eau de Parfum",
    "gender": "Women",
    "price": "€89",
    "launchYear": 2020,
    "perfumer": "Annick Ménardo",
    "topNotes": ["Apple", "Plum", "Blackcurrant"],
    "heartNotes": ["Jasmine Sambac", "Thyme", "Olive Blossom"],
    "baseNotes": ["Sandalwood", "Cedar", "Vanilla"],
    "family": "Floral Woody",
    "longevity": "6-8 hours",
    "sillage": "Moderate",
    "seasons": ["Spring", "Summer", "Fall"],
    "occasions": ["Office", "Casual", "Date Night"],
    "targetAudience": "Modern professional women who value authenticity",
    "keyMessage": "Celebrates the active, authentic woman"
}

# Données Chanel N°5
chanel_no5 = {
    "brand": "Chanel",
    "productName": "N°5",
    "concentration": "Eau de Parfum",
    "gender": "Women",
    "price": "€135",
    "launchYear": 1921,
    "perfumer": "Ernest Beaux",
    "topNotes": ["Aldehydes", "Neroli", "Ylang-Ylang", "Bergamot"],
    "heartNotes": ["Rose", "Jasmine", "Lily of the Valley", "Iris"],
    "baseNotes": ["Sandalwood", "Vetiver", "Vanilla", "Amber", "Musk"],
    "family": "Floral Aldehydic",
    "longevity": "8-12 hours",
    "sillage": "Heavy",
    "seasons": ["Fall", "Winter", "Spring"],
    "occasions": ["Evening", "Special Occasions", "Formal"],
    "targetAudience": "Women who appreciate timeless elegance and classic luxury",
    "keyMessage": "The world's most iconic fragrance, a timeless masterpiece",
    "funFact": "Marilyn Monroe famously said she wore 'five drops of Chanel No. 5' to bed"
}

if __name__ == "__main__":
    import sys
    
    perfume = sys.argv[1] if len(sys.argv) > 1 else "boss-alive"
    lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    
    data = boss_alive if perfume == "boss-alive" else chanel_no5
    
    print(f"Generating {perfume} review in {lang} with Claude Sonnet 4.5...")
    review = generate_perfume_review(data, lang)
    
    output_path = f"/home/ubuntu/hbb/content/{lang}/perfumes/{perfume}.md"
    with open(output_path, 'w') as f:
        f.write(review)
    
    print(f"✅ {perfume} {lang.upper()} generated: {output_path}")
