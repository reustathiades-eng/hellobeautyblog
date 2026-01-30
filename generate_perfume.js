const Anthropic = require('@anthropic-ai/sdk').default;
const fs = require('fs');

const client = new Anthropic();

async function generatePerfumeReview(perfumeData, language = 'en') {
    const brief = fs.readFileSync('/home/ubuntu/hbb/PERFUME_BRIEF.md', 'utf8');
    
    const prompt = `You are an expert perfume reviewer for HelloBeautyBlog.com. Generate a complete perfume review in ${language === 'en' ? 'English' : language} following the brief below.

BRIEF:
${brief}

PERFUME DATA:
${JSON.stringify(perfumeData, null, 2)}

Generate a complete Hugo markdown file with:
1. Full YAML front matter with all fields
2. Engaging, professional content (800-1200 words)
3. Personal experience and sensory descriptions
4. SEO-optimized but natural writing

Output ONLY the markdown file content, starting with --- for the front matter.`;

    const response = await client.messages.create({
        model: "claude-sonnet-4-5-20250514",
        max_tokens: 4000,
        messages: [{ role: "user", content: prompt }]
    });

    return response.content[0].text;
}

// Données Boss Alive
const bossAlive = {
    brand: "Hugo Boss",
    productName: "Boss Alive",
    concentration: "Eau de Parfum",
    gender: "Women",
    price: "€89",
    launchYear: 2020,
    perfumer: "Annick Ménardo",
    topNotes: ["Apple", "Plum", "Blackcurrant"],
    heartNotes: ["Jasmine Sambac", "Thyme", "Olive Blossom"],
    baseNotes: ["Sandalwood", "Cedar", "Vanilla"],
    family: "Floral Woody",
    longevity: "6-8 hours",
    sillage: "Moderate",
    seasons: ["Spring", "Summer", "Fall"],
    occasions: ["Office", "Casual", "Date Night"],
    targetAudience: "Modern professional women who value authenticity",
    keyMessage: "Celebrates the active, authentic woman"
};

async function main() {
    console.log("Generating Boss Alive review with Claude Sonnet 4.5...");
    const review = await generatePerfumeReview(bossAlive, 'en');
    fs.writeFileSync('/home/ubuntu/hbb/content/en/perfumes/boss-alive-new.md', review);
    console.log("✅ Boss Alive EN generated!");
}

main().catch(console.error);
