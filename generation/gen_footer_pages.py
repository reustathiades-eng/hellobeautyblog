#!/usr/bin/env python3
import json, os, time, urllib.request

os.chdir("/home/ubuntu/hbb")
API_KEY = open(".secrets").read().strip()

LANGS = [
    ("en","English"),("fr","French"),("de","German"),("es","Spanish"),
    ("it","Italian"),("pt","Portuguese"),("nl","Dutch"),("pl","Polish"),
    ("tr","Turkish"),("ja","Japanese"),("ko","Korean"),("zh","Chinese"),
    ("ar","Arabic"),("hi","Hindi")
]

PAGES = {
    "about": {
        "title_en": "About Us",
        "key": "page-about",
        "prompt": """Write a compelling About Us page for hellobeautyblog.com in {lname}.

The site is a multilingual beauty blog covering perfumes, skincare, makeup and haircare across 14 languages.
Founded by a team of passionate beauty experts based across Europe and Asia.
Our 4 experts: Sophie Laurent (perfume, Paris/Grasse), Emma Chen (skincare, Seoul/NYC), Isabella Romano (makeup, Milan), Olivia Taylor (haircare, London).
Mission: make expert beauty knowledge accessible worldwide in readers' native languages.
Values: honesty in reviews, science-backed advice, inclusivity, sustainability awareness.

Write 500-700 words. Warm, professional, trustworthy tone.
Include keywords: beauty blog, expert reviews, skincare tips, perfume guide, makeup tutorials, haircare advice.
Structure with 3-4 H2 sections (Our Story, Our Team, Our Mission/Values, etc.).
Mention the multilingual aspect as a key differentiator.
Do NOT include frontmatter. Return ONLY the markdown body content."""
    },
    "contact": {
        "title_en": "Contact",
        "key": "page-contact",
        "prompt": """Write a Contact page for hellobeautyblog.com in {lname}.

This is a beauty blog. The contact page should:
- Welcome readers to get in touch
- List contact reasons: press inquiries, brand collaborations, product reviews, advertising, general questions
- Provide email: hello@hellobeautyblog.com
- Mention typical response time (48 hours)
- Include a note about brand partnerships and PR samples
- Mention social media presence

Write 250-350 words. Friendly, professional tone.
Structure with 2-3 H2 sections.
Do NOT include frontmatter. Return ONLY the markdown body content."""
    },
    "privacy": {
        "title_en": "Privacy Policy",
        "key": "page-privacy",
        "prompt": """Write a Privacy Policy page for hellobeautyblog.com in {lname}.

This is a beauty blog that:
- Uses cookies for analytics (Google Analytics) and advertising
- May use affiliate links (Amazon, Sephora, etc.)
- Has a newsletter signup (email collection)
- Does NOT sell user data
- Is hosted on Cloudflare Pages
- Complies with GDPR (European visitors) and CCPA

Write a complete, credible privacy policy. 800-1200 words.
Professional legal tone but readable.
Structure with clear H2 sections: Information We Collect, How We Use It, Cookies, Third-Party Services, Affiliate Links, Your Rights, Data Retention, Children's Privacy, Changes to Policy, Contact.
Include the effective date as January 1, 2025.
Do NOT include frontmatter. Return ONLY the markdown body content."""
    },
    "terms": {
        "title_en": "Terms of Use",
        "key": "page-terms",
        "prompt": """Write Terms of Use for hellobeautyblog.com in {lname}.

This is a beauty blog. Terms should cover:
- Acceptance of terms by using the site
- Intellectual property (all content is owned by HelloBeautyBlog)
- User conduct
- Disclaimer: content is for informational purposes, not medical/professional advice
- Affiliate links disclosure
- Limitation of liability
- Product reviews reflect personal opinions
- External links disclaimer
- Governing law (France/EU)
- Changes to terms
- Effective date: January 1, 2025

Write 600-900 words. Professional legal tone but accessible.
Structure with clear H2 sections.
Do NOT include frontmatter. Return ONLY the markdown body content."""
    }
}

# Frontmatter translations
TITLES = {
    "about": {
        "en":"About Us","fr":"À propos","de":"Über uns","es":"Sobre nosotros",
        "it":"Chi siamo","pt":"Sobre nós","nl":"Over ons","pl":"O nas",
        "tr":"Hakkımızda","ja":"私たちについて","ko":"소개","zh":"关于我们",
        "ar":"من نحن","hi":"हमारे बारे में"
    },
    "contact": {
        "en":"Contact","fr":"Contact","de":"Kontakt","es":"Contacto",
        "it":"Contatti","pt":"Contato","nl":"Contact","pl":"Kontakt",
        "tr":"İletişim","ja":"お問い合わせ","ko":"연락처","zh":"联系我们",
        "ar":"اتصل بنا","hi":"संपर्क"
    },
    "privacy": {
        "en":"Privacy Policy","fr":"Politique de confidentialité","de":"Datenschutzrichtlinie","es":"Política de privacidad",
        "it":"Informativa sulla privacy","pt":"Política de privacidade","nl":"Privacybeleid","pl":"Polityka prywatności",
        "tr":"Gizlilik Politikası","ja":"プライバシーポリシー","ko":"개인정보처리방침","zh":"隐私政策",
        "ar":"سياسة الخصوصية","hi":"गोपनीयता नीति"
    },
    "terms": {
        "en":"Terms of Use","fr":"Conditions d'utilisation","de":"Nutzungsbedingungen","es":"Términos de uso",
        "it":"Termini di utilizzo","pt":"Termos de uso","nl":"Gebruiksvoorwaarden","pl":"Regulamin",
        "tr":"Kullanım Koşulları","ja":"利用規約","ko":"이용약관","zh":"使用条款",
        "ar":"شروط الاستخدام","hi":"उपयोग की शर्तें"
    }
}

DESCS = {
    "about": {
        "en":"Learn about HelloBeautyBlog, our mission and our team of beauty experts.",
        "fr":"Découvrez HelloBeautyBlog, notre mission et notre équipe d'experts beauté.",
        "de":"Erfahren Sie mehr über HelloBeautyBlog, unsere Mission und unser Expertenteam.",
        "es":"Conoce HelloBeautyBlog, nuestra misión y nuestro equipo de expertos en belleza.",
        "it":"Scopri HelloBeautyBlog, la nostra missione e il nostro team di esperti di bellezza.",
        "pt":"Conheça o HelloBeautyBlog, nossa missão e nossa equipe de especialistas em beleza.",
        "nl":"Ontdek HelloBeautyBlog, onze missie en ons team van beauty-experts.",
        "pl":"Poznaj HelloBeautyBlog, naszą misję i zespół ekspertów od urody.",
        "tr":"HelloBeautyBlog'u, misyonumuzu ve güzellik uzmanları ekibimizi tanıyın.",
        "ja":"HelloBeautyBlogについて、私たちのミッションとビューティー専門家チームをご紹介します。",
        "ko":"HelloBeautyBlog의 미션과 뷰티 전문가 팀을 소개합니다.",
        "zh":"了解HelloBeautyBlog、我们的使命和美容专家团队。",
        "ar":"تعرف على HelloBeautyBlog ومهمتنا وفريق خبراء الجمال لدينا.",
        "hi":"HelloBeautyBlog, हमारे मिशन और हमारी ब्यूटी विशेषज्ञों की टीम के बारे में जानें।"
    }
}

done = 0
errors = 0

for page_key, page_data in PAGES.items():
    for lang, lname in LANGS:
        target = f"content/{lang}/{page_key}.md"
        
        if os.path.exists(target) and os.path.getsize(target) > 500:
            print(f"[SKIP] {page_key}/{lang}")
            done += 1
            continue

        print(f"[GEN] {page_key}/{lang} ({lname})...", flush=True)

        prompt = page_data["prompt"].format(lname=lname)

        payload = json.dumps({
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 3000,
            "messages": [{"role": "user", "content": prompt}]
        })

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload.encode(),
            headers={
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            body = data["content"][0]["text"].strip()
            if body.startswith("```"):
                body = body.split("\n", 1)[1]
            if body.endswith("```"):
                body = body.rsplit("```", 1)[0].strip()

            title = TITLES.get(page_key, {}).get(lang, page_data["title_en"])
            desc = DESCS.get(page_key, {}).get(lang, "")
            desc_line = f'\ndescription: "{desc}"' if desc else ""

            frontmatter = f"""---
title: "{title}"
translationKey: "{page_data['key']}"{desc_line}
layout: "single"
---

"""
            with open(target, "w", encoding="utf-8") as f:
                f.write(frontmatter + body + "\n")
            
            done += 1
            size = os.path.getsize(target)
            print(f"  ✅ {page_key}/{lang} ({size}B) done:{done}", flush=True)
        except Exception as e:
            print(f"  ❌ {page_key}/{lang}: {e}", flush=True)
            errors += 1

        time.sleep(2)

print(f"\n=== DONE: {done} ok, {errors} errors ===", flush=True)

os.system('cd /home/ubuntu/hbb && git add content/*/about.md content/*/contact.md content/*/privacy.md content/*/terms.md && git commit -m "feat: complete footer pages content (about/contact/privacy/terms) 14 langs" && git push origin main')
print("=== PUSHED ===")
