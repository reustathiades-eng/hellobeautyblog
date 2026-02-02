#!/usr/bin/env python3
"""Create 51 perfume subcategory _index.md files for all 13 non-EN languages."""
import os

# Perfume section folder name per language
SECTION_DIRS = {
    "fr": "parfums", "de": "parfum", "es": "perfumes", "it": "profumi",
    "pt": "perfumes", "nl": "parfum", "pl": "perfumy", "tr": "parfum",
    "ja": "perfumes", "ko": "perfumes", "zh": "perfumes", "ar": "perfumes", "hi": "perfumes"
}

# === GENDER TRANSLATIONS ===
GENDER = {
    "women": {
        "fr": ("Parfums Femme", "Découvrez notre collection de parfums pour femme, des floraux intemporels aux orientaux modernes."),
        "de": ("Damenparfums", "Entdecken Sie unsere Kollektion der feinsten Damenparfums, von zeitlosen Blumendüften bis zu modernen Orientalen."),
        "es": ("Perfumes de Mujer", "Descubre nuestra colección de perfumes femeninos, desde florales atemporales hasta orientales modernos."),
        "it": ("Profumi Donna", "Scopri la nostra collezione di profumi femminili, dai floreali senza tempo agli orientali moderni."),
        "pt": ("Perfumes Femininos", "Descubra nossa coleção de perfumes femininos, de florais atemporais a orientais modernos."),
        "nl": ("Damesparfums", "Ontdek onze collectie van de mooiste damesparfums, van tijdloze bloemige tot moderne oosterse geuren."),
        "pl": ("Perfumy Damskie", "Odkryj naszą kolekcję najlepszych perfum damskich, od ponadczasowych kwiatowych po nowoczesne orientalne."),
        "tr": ("Kadın Parfümleri", "En iyi kadın parfümlerinden oluşan koleksiyonumuzu keşfedin."),
        "ja": ("レディース香水", "時代を超えたフローラルからモダンなオリエンタルまで、厳選されたレディース香水コレクション。"),
        "ko": ("여성 향수", "시대를 초월한 플로럴부터 모던 오리엔탈까지, 엄선된 여성 향수 컬렉션."),
        "zh": ("女士香水", "探索我们精选的女士香水系列，从经典花香到现代东方香调。"),
        "ar": ("عطور نسائية", "اكتشفي مجموعتنا من أرقى العطور النسائية."),
        "hi": ("महिला इत्र", "शाश्वत पुष्प से आधुनिक ओरिएंटल तक, हमारे क्यूरेटेड महिला इत्र संग्रह की खोज करें।"),
    },
    "men": {
        "fr": ("Parfums Homme", "Explorez notre sélection de parfums masculins distingués, des aquatiques frais aux boisés audacieux."),
        "de": ("Herrenparfums", "Entdecken Sie unsere Auswahl an distinguierten Herrenparfums, von frischen Aquatischen bis zu kühnen Holzdüften."),
        "es": ("Perfumes de Hombre", "Explora nuestra selección de perfumes masculinos distinguidos, desde acuáticos frescos hasta amaderados audaces."),
        "it": ("Profumi Uomo", "Esplora la nostra selezione di profumi maschili distinti, dai freschi acquatici ai legnosi audaci."),
        "pt": ("Perfumes Masculinos", "Explore nossa seleção de perfumes masculinos distintos, de aquáticos frescos a amadeirados ousados."),
        "nl": ("Herenparfums", "Ontdek onze selectie van verfijnde herenparfums, van frisse aquatische tot stoere houtachtige geuren."),
        "pl": ("Perfumy Męskie", "Odkryj nasz wybór wyrafinowanych perfum męskich, od świeżych wodnych po odważne drzewne."),
        "tr": ("Erkek Parfümleri", "Seçkin erkek parfümlerimizi keşfedin, taze akuatik notalardan cesur odunsu kokulara."),
        "ja": ("メンズ香水", "フレッシュアクアティックからボールドウッディまで、厳選されたメンズ香水コレクション。"),
        "ko": ("남성 향수", "프레시 아쿠아틱부터 볼드 우디까지, 엄선된 남성 향수 컬렉션."),
        "zh": ("男士香水", "探索我们精选的男士香水系列，从清新水生到大胆木质香调。"),
        "ar": ("عطور رجالية", "اكتشف مجموعتنا من العطور الرجالية المميزة."),
        "hi": ("पुरुष इत्र", "ताज़ा एक्वाटिक से बोल्ड वुडी तक, हमारे विशिष्ट पुरुष इत्र संग्रह का अन्वेषण करें।"),
    },
    "unisex": {
        "fr": ("Parfums Unisexes", "Parcourez notre collection de parfums non-genrés qui transcendent les frontières."),
        "de": ("Unisex-Parfums", "Entdecken Sie unsere Kollektion geschlechtsneutraler Düfte, die Grenzen überschreiten."),
        "es": ("Perfumes Unisex", "Explora nuestra colección de fragancias de género neutro que trascienden fronteras."),
        "it": ("Profumi Unisex", "Scopri la nostra collezione di fragranze gender-neutral che trascendono i confini."),
        "pt": ("Perfumes Unissex", "Explore nossa coleção de fragrâncias neutras que transcendem fronteiras."),
        "nl": ("Unisex Parfums", "Ontdek onze collectie van genderneutrale geuren die grenzen overschrijden."),
        "pl": ("Perfumy Unisex", "Odkryj naszą kolekcję perfum unisex, które przekraczają granice."),
        "tr": ("Unisex Parfümler", "Sınırları aşan cinsiyet ayrımı gözetmeyen parfüm koleksiyonumuzu keşfedin."),
        "ja": ("ユニセックス香水", "境界を超えるジェンダーニュートラルな香水コレクション。"),
        "ko": ("유니섹스 향수", "경계를 초월하는 젠더 뉴트럴 향수 컬렉션."),
        "zh": ("中性香水", "探索我们超越性别界限的中性香水系列。"),
        "ar": ("عطور للجنسين", "اكتشف مجموعتنا من العطور المحايدة التي تتجاوز الحدود."),
        "hi": ("यूनिसेक्स इत्र", "सीमाओं को पार करने वाले जेंडर-न्यूट्रल इत्र संग्रह का अन्वेषण करें।"),
    },
}

# === FAMILY TRANSLATIONS ===
FAMILY = {
    "floral": {
        "fr": ("Parfums Floraux", "Explorez notre collection de parfums floraux, de la rose délicate au jasmin exotique."),
        "de": ("Blumige Parfums", "Entdecken Sie unsere Kollektion blumiger Düfte, von zarter Rose bis zu exotischem Jasmin."),
        "es": ("Perfumes Florales", "Explora nuestra colección de fragancias florales, desde la rosa delicada hasta el jazmín exótico."),
        "it": ("Profumi Floreali", "Esplora la nostra collezione di fragranze floreali, dalla rosa delicata al gelsomino esotico."),
        "pt": ("Perfumes Florais", "Explore nossa coleção de fragrâncias florais, da rosa delicada ao jasmim exótico."),
        "nl": ("Bloemige Parfums", "Ontdek onze collectie bloemige geuren, van delicate roos tot exotische jasmijn."),
        "pl": ("Perfumy Kwiatowe", "Odkryj naszą kolekcję kwiatowych zapachów, od delikatnej róży po egzotyczny jaśmin."),
        "tr": ("Çiçeksi Parfümler", "Narin gülden egzotik yasemina, çiçeksi parfüm koleksiyonumuzu keşfedin."),
        "ja": ("フローラル香水", "繊細なローズからエキゾチックなジャスミンまで、フローラル香水コレクション。"),
        "ko": ("플로럴 향수", "섬세한 장미부터 이국적인 재스민까지, 플로럴 향수 컬렉션."),
        "zh": ("花香调香水", "探索我们的花香调香水系列，从精致的玫瑰到异域茉莉。"),
        "ar": ("عطور زهرية", "اكتشف مجموعتنا من العطور الزهرية، من الورد الرقيق إلى الياسمين الغريب."),
        "hi": ("फ्लोरल इत्र", "नाजुक गुलाब से विदेशी चमेली तक, फ्लोरल इत्र संग्रह।"),
    },
    "oriental": {
        "fr": ("Parfums Orientaux", "Découvrez les fragrances orientales riches et opulentes aux notes de vanille, ambre et épices."),
        "de": ("Orientalische Parfums", "Entdecken Sie reiche orientalische Düfte mit warmen Noten von Vanille, Amber und Gewürzen."),
        "es": ("Perfumes Orientales", "Descubre fragancias orientales ricas y opulentas con notas de vainilla, ámbar y especias."),
        "it": ("Profumi Orientali", "Scopri fragranze orientali ricche e opulente con note di vaniglia, ambra e spezie."),
        "pt": ("Perfumes Orientais", "Descubra fragrâncias orientais ricas e opulentas com notas de baunilha, âmbar e especiarias."),
        "nl": ("Oosterse Parfums", "Ontdek rijke oosterse geuren met warme tonen van vanille, amber en kruiden."),
        "pl": ("Perfumy Orientalne", "Odkryj bogate orientalne zapachy z nutami wanilii, ambry i przypraw."),
        "tr": ("Oryantal Parfümler", "Vanilya, amber ve egzotik baharat notalarıyla zengin oryantal kokuları keşfedin."),
        "ja": ("オリエンタル香水", "バニラ、アンバー、エキゾチックなスパイスの温かみのあるオリエンタル香水。"),
        "ko": ("오리엔탈 향수", "바닐라, 앰버, 이국적인 스파이스의 따뜻한 오리엔탈 향수."),
        "zh": ("东方调香水", "探索我们的东方调香水系列，蕴含香草、琥珀和异域香料。"),
        "ar": ("عطور شرقية", "اكتشف العطور الشرقية الفاخرة بنوتات الفانيلا والعنبر والتوابل."),
        "hi": ("ओरिएंटल इत्र", "वेनिला, एम्बर और विदेशी मसालों के साथ समृद्ध ओरिएंटल इत्र।"),
    },
    "woody": {
        "fr": ("Parfums Boisés", "Parcourez notre collection de parfums boisés au santal, cèdre et vétiver."),
        "de": ("Holzige Parfums", "Entdecken Sie unsere Kollektion holziger Düfte mit Sandelholz, Zeder und Vetiver."),
        "es": ("Perfumes Amaderados", "Explora nuestra colección de fragancias amaderadas con sándalo, cedro y vetiver."),
        "it": ("Profumi Legnosi", "Esplora la nostra collezione di fragranze legnose con sandalo, cedro e vetiver."),
        "pt": ("Perfumes Amadeirados", "Explore nossa coleção de fragrâncias amadeiradas com sândalo, cedro e vetiver."),
        "nl": ("Houtachtige Parfums", "Ontdek onze collectie houtachtige geuren met sandelhout, ceder en vetiver."),
        "pl": ("Perfumy Drzewne", "Odkryj naszą kolekcję drzewnych zapachów z drzewem sandałowym, cedrem i wetiwer."),
        "tr": ("Odunsu Parfümler", "Sandal ağacı, sedir ve vetiver ile odunsu parfüm koleksiyonumuzu keşfedin."),
        "ja": ("ウッディ香水", "サンダルウッド、シダー、ベチバーのウッディ香水コレクション。"),
        "ko": ("우디 향수", "샌달우드, 시더, 베티버의 우디 향수 컬렉션."),
        "zh": ("木质调香水", "探索我们的木质调香水系列，蕴含檀香、雪松和香根草。"),
        "ar": ("عطور خشبية", "اكتشف مجموعتنا من العطور الخشبية بنوتات خشب الصندل والأرز والفيتيفر."),
        "hi": ("वुडी इत्र", "चंदन, देवदार और वेटिवर के साथ वुडी इत्र संग्रह।"),
    },
    "fresh": {
        "fr": ("Parfums Frais", "Découvrez des fragrances fraîches vivifiantes aux notes d'agrumes, aquatiques et vertes."),
        "de": ("Frische Parfums", "Entdecken Sie belebende frische Düfte mit Zitrus-, Aquatischen und Grünen Noten."),
        "es": ("Perfumes Frescos", "Descubre fragancias frescas vigorizantes con notas cítricas, acuáticas y verdes."),
        "it": ("Profumi Freschi", "Scopri fragranze fresche e tonificanti con note agrumate, acquatiche e verdi."),
        "pt": ("Perfumes Frescos", "Descubra fragrâncias frescas revigorantes com notas cítricas, aquáticas e verdes."),
        "nl": ("Frisse Parfums", "Ontdek verkwikkende frisse geuren met citrus-, aquatische en groene noten."),
        "pl": ("Perfumy Świeże", "Odkryj orzeźwiające świeże zapachy z nutami cytrusowymi, wodnymi i zielonymi."),
        "tr": ("Taze Parfümler", "Narenciye, akuatik ve yeşil notalarla canlandırıcı taze kokuları keşfedin."),
        "ja": ("フレッシュ香水", "シトラス、アクアティック、グリーンノートの爽やかなフレッシュ香水。"),
        "ko": ("프레시 향수", "시트러스, 아쿠아틱, 그린 노트의 상쾌한 프레시 향수."),
        "zh": ("清新调香水", "探索我们的清新调香水系列，蕴含柑橘、水生和绿色香调。"),
        "ar": ("عطور منعشة", "اكتشف عطوراً منعشة بنوتات الحمضيات والمائية والخضراء."),
        "hi": ("फ्रेश इत्र", "सिट्रस, एक्वाटिक और ग्रीन नोट्स के साथ ताज़ा इत्र।"),
    },
    "aromatic": {
        "fr": ("Parfums Aromatiques", "Explorez les parfums aromatiques mêlant herbes, lavande et épices."),
        "de": ("Aromatische Parfums", "Entdecken Sie aromatische Düfte, die Kräuter, Lavendel und Gewürze vereinen."),
        "es": ("Perfumes Aromáticos", "Explora fragancias aromáticas que mezclan hierbas, lavanda y especias."),
        "it": ("Profumi Aromatici", "Esplora fragranze aromatiche che fondono erbe, lavanda e spezie."),
        "pt": ("Perfumes Aromáticos", "Explore fragrâncias aromáticas que misturam ervas, lavanda e especiarias."),
        "nl": ("Aromatische Parfums", "Ontdek aromatische geuren die kruiden, lavendel en specerijen combineren."),
        "pl": ("Perfumy Aromatyczne", "Odkryj aromatyczne zapachy łączące zioła, lawendę i przyprawy."),
        "tr": ("Aromatik Parfümler", "Bitki, lavanta ve baharatları harmanlayan aromatik kokuları keşfedin."),
        "ja": ("アロマティック香水", "ハーブ、ラベンダー、スパイスを融合したアロマティック香水。"),
        "ko": ("아로마틱 향수", "허브, 라벤더, 스파이스를 블렌딩한 아로마틱 향수."),
        "zh": ("芳香调香水", "探索融合草本、薰衣草和香料的芳香调香水。"),
        "ar": ("عطور عطرية", "اكتشف العطور العطرية التي تمزج الأعشاب والخزامى والبهارات."),
        "hi": ("एरोमैटिक इत्र", "जड़ी-बूटियों, लैवेंडर और मसालों को मिलाने वाले एरोमैटिक इत्र।"),
    },
    "chypre": {
        "fr": ("Parfums Chyprés", "Découvrez le monde élégant des parfums chyprés, construits sur la mousse de chêne et le bergamote."),
        "de": ("Chypre Parfums", "Entdecken Sie die elegante Welt der Chypre-Düfte, aufgebaut auf Eichenmoos und Bergamotte."),
        "es": ("Perfumes Chipre", "Descubre el elegante mundo de las fragancias chipre, construidas sobre musgo de roble y bergamota."),
        "it": ("Profumi Cipriati", "Scopri l'elegante mondo dei profumi cipriati, costruiti su muschio di quercia e bergamotto."),
        "pt": ("Perfumes Chipre", "Descubra o elegante mundo das fragrâncias chipre, construídas sobre musgo de carvalho e bergamota."),
        "nl": ("Chypre Parfums", "Ontdek de elegante wereld van chypre-geuren, gebouwd op eikenmos en bergamot."),
        "pl": ("Perfumy Chypre", "Odkryj elegancki świat perfum chypre, zbudowanych na mchu dębowym i bergamotce."),
        "tr": ("Chypre Parfümler", "Meşe yosunu ve bergamot üzerine inşa edilmiş chypre kokuları keşfedin."),
        "ja": ("シプレ香水", "オークモスとベルガモットを基調としたシプレ香水の世界。"),
        "ko": ("시프레 향수", "오크모스와 베르가못을 기반으로 한 시프레 향수의 세계."),
        "zh": ("西普调香水", "探索以橡木苔和佛手柑为基础的西普调香水世界。"),
        "ar": ("عطور شيبر", "اكتشف عالم عطور الشيبر الأنيقة المبنية على طحلب البلوط والبرغموت."),
        "hi": ("शिप्र इत्र", "ओक मॉस और बरगामोट पर निर्मित शिप्र इत्र की सुरुचिपूर्ण दुनिया।"),
    },
    "gourmand": {
        "fr": ("Parfums Gourmands", "Craquez pour des fragrances gourmandes aux notes de vanille, chocolat et café."),
        "de": ("Gourmand Parfums", "Genießen Sie köstliche Gourmand-Düfte mit Noten von Vanille, Schokolade und Kaffee."),
        "es": ("Perfumes Gourmand", "Disfruta de deliciosas fragancias gourmand con notas de vainilla, chocolate y café."),
        "it": ("Profumi Gourmand", "Lasciati tentare da fragranze gourmand con note di vaniglia, cioccolato e caffè."),
        "pt": ("Perfumes Gourmand", "Delicie-se com fragrâncias gourmand com notas de baunilha, chocolate e café."),
        "nl": ("Gourmand Parfums", "Geniet van heerlijke gourmand-geuren met noten van vanille, chocolade en koffie."),
        "pl": ("Perfumy Gourmand", "Delektuj się perfumami gourmand z nutami wanilii, czekolady i kawy."),
        "tr": ("Gurme Parfümler", "Vanilya, çikolata ve kahve notalarıyla gurme kokuları keşfedin."),
        "ja": ("グルマン香水", "バニラ、チョコレート、コーヒーのグルマン香水コレクション。"),
        "ko": ("구르망 향수", "바닐라, 초콜릿, 커피의 구르망 향수 컬렉션."),
        "zh": ("美食调香水", "沉浸在香草、巧克力和咖啡的美食调香水中。"),
        "ar": ("عطور الذواقة", "استمتع بعطور الذواقة اللذيذة بنوتات الفانيلا والشوكولاتة والقهوة."),
        "hi": ("गॉरमंड इत्र", "वेनिला, चॉकलेट और कॉफ़ी के साथ गॉरमंड इत्र।"),
    },
}

# === OCCASION TRANSLATIONS ===
OCCASION = {
    "everyday": {
        "fr": ("Parfums du Quotidien", "Trouvez votre parfum idéal pour tous les jours, des senteurs polyvalentes et confortables."),
        "de": ("Alltagsparfums", "Finden Sie Ihren perfekten Alltagsduft — vielseitige und komfortable Düfte."),
        "es": ("Perfumes para el Día a Día", "Encuentra tu fragancia perfecta para el día a día, aromas versátiles y cómodos."),
        "it": ("Profumi Quotidiani", "Trova il tuo profumo quotidiano ideale, fragranze versatili e confortevoli."),
        "pt": ("Perfumes para o Dia a Dia", "Encontre sua fragrância perfeita para o dia a dia, aromas versáteis e confortáveis."),
        "nl": ("Alledaagse Parfums", "Vind uw perfecte alledaagse geur — veelzijdige en comfortabele parfums."),
        "pl": ("Perfumy na Co Dzień", "Znajdź swój idealny codzienny zapach — wszechstronne i komfortowe perfumy."),
        "tr": ("Günlük Parfümler", "Günlük kullanım için mükemmel parfümünüzü bulun."),
        "ja": ("デイリー香水", "毎日使える万能で心地よいデイリー香水を見つけよう。"),
        "ko": ("데일리 향수", "매일 사용할 수 있는 다재다능하고 편안한 데일리 향수."),
        "zh": ("日常香水", "找到您完美的日常香水——百搭舒适的香调。"),
        "ar": ("عطور يومية", "اعثر على عطرك المثالي لكل يوم."),
        "hi": ("रोज़मर्रा का इत्र", "हर दिन के लिए अपना आदर्श इत्र खोजें।"),
    },
    "evening": {
        "fr": ("Parfums de Soirée", "Découvrez des fragrances captivantes qui marquent les esprits après le coucher du soleil."),
        "de": ("Abendparfums", "Entdecken Sie fesselnde Abendparfums, die nach Sonnenuntergang beeindrucken."),
        "es": ("Perfumes de Noche", "Descubre fragancias cautivadoras que dejan una impresión duradera por la noche."),
        "it": ("Profumi da Sera", "Scopri fragranze affascinanti che lasciano un'impressione duratura dopo il tramonto."),
        "pt": ("Perfumes Noturnos", "Descubra fragrâncias cativantes que deixam uma impressão duradoura após o anoitecer."),
        "nl": ("Avondparfums", "Ontdek betoverende avondparfums die een blijvende indruk maken."),
        "pl": ("Perfumy Wieczorowe", "Odkryj urzekające wieczorowe zapachy, które robią wrażenie."),
        "tr": ("Akşam Parfümleri", "Gün batımından sonra kalıcı bir izlenim bırakan büyüleyici akşam kokuları."),
        "ja": ("イブニング香水", "夜に印象を残す魅惑的なイブニング香水コレクション。"),
        "ko": ("이브닝 향수", "해가 진 후 강렬한 인상을 남기는 매혹적인 이브닝 향수."),
        "zh": ("晚间香水", "探索日落后留下深刻印象的迷人晚间香水。"),
        "ar": ("عطور مسائية", "اكتشف عطوراً أخّاذة تترك انطباعاً دائماً في المساء."),
        "hi": ("शाम के इत्र", "सूर्यास्त के बाद स्थायी प्रभाव छोड़ने वाले मनमोहक शाम के इत्र।"),
    },
    "romantic": {
        "fr": ("Parfums Romantiques", "Explorez des fragrances séduisantes pour les soirées en amoureux et les occasions spéciales."),
        "de": ("Romantische Parfums", "Entdecken Sie verführerische Düfte für romantische Abende und besondere Anlässe."),
        "es": ("Perfumes Románticos", "Explora fragancias seductoras para citas nocturnas y ocasiones especiales."),
        "it": ("Profumi Romantici", "Esplora fragranze seducenti per serate romantiche e occasioni speciali."),
        "pt": ("Perfumes Românticos", "Explore fragrâncias sedutoras para encontros românticos e ocasiões especiais."),
        "nl": ("Romantische Parfums", "Ontdek verleidelijke geuren voor romantische avonden en speciale gelegenheden."),
        "pl": ("Perfumy Romantyczne", "Odkryj uwodzicielskie zapachy na romantyczne randki i specjalne okazje."),
        "tr": ("Romantik Parfümler", "Romantik geceler ve özel anlar için baştan çıkarıcı kokular."),
        "ja": ("ロマンティック香水", "デートナイトや特別な日のための魅惑的なロマンティック香水。"),
        "ko": ("로맨틱 향수", "데이트와 특별한 날을 위한 매혹적인 로맨틱 향수."),
        "zh": ("浪漫香水", "探索约会之夜和特殊场合的诱人浪漫香水。"),
        "ar": ("عطور رومانسية", "اكتشف عطوراً فاتنة للأمسيات الرومانسية والمناسبات الخاصة."),
        "hi": ("रोमांटिक इत्र", "डेट नाइट और विशेष अवसरों के लिए मोहक रोमांटिक इत्र।"),
    },
    "office": {
        "fr": ("Parfums de Bureau", "Des parfums professionnels, raffinés et subtils, adaptés au milieu de travail."),
        "de": ("Büro-Parfums", "Professionelle, raffinierte und dezente Düfte für den Arbeitsplatz."),
        "es": ("Perfumes de Oficina", "Fragancias profesionales, refinadas y sutiles, apropiadas para la oficina."),
        "it": ("Profumi da Ufficio", "Fragranze professionali, raffinate e sottili, appropriate per l'ufficio."),
        "pt": ("Perfumes para Escritório", "Fragrâncias profissionais, refinadas e sutis, apropriadas para o escritório."),
        "nl": ("Kantoorparfums", "Professionele, verfijnde en subtiele geuren voor op de werkplek."),
        "pl": ("Perfumy do Biura", "Profesjonalne, wyrafinowane i subtelne zapachy odpowiednie do biura."),
        "tr": ("Ofis Parfümleri", "İş yerine uygun profesyonel, zarif ve ince kokular."),
        "ja": ("オフィス香水", "洗練された上品なオフィス向け香水コレクション。"),
        "ko": ("오피스 향수", "세련되고 은은한 직장용 오피스 향수 컬렉션."),
        "zh": ("办公室香水", "专业、精致、低调的办公室香水系列。"),
        "ar": ("عطور المكتب", "عطور مهنية، أنيقة ورقيقة مناسبة لمكان العمل."),
        "hi": ("ऑफिस इत्र", "कार्यस्थल के लिए पेशेवर, परिष्कृत और सूक्ष्म इत्र।"),
    },
    "summer": {
        "fr": ("Parfums d'Été", "Des fragrances rafraîchissantes aux notes légères et aériennes, parfaites pour les beaux jours."),
        "de": ("Sommerparfums", "Erfrischende Sommerdüfte mit leichten, luftigen Noten für warmes Wetter."),
        "es": ("Perfumes de Verano", "Fragancias refrescantes con notas ligeras y brisas, perfectas para el calor."),
        "it": ("Profumi Estivi", "Fragranze rinfrescanti con note leggere e ariose, perfette per il caldo."),
        "pt": ("Perfumes de Verão", "Fragrâncias refrescantes com notas leves e arejadas, perfeitas para o calor."),
        "nl": ("Zomerparfums", "Verfrissende zomergeuren met lichte, luchtige noten voor warm weer."),
        "pl": ("Perfumy Letnie", "Orzeźwiające letnie zapachy z lekkimi, przewiewnymi nutami na ciepłe dni."),
        "tr": ("Yaz Parfümleri", "Sıcak hava için hafif, ferah notalarla canlandırıcı yaz kokuları."),
        "ja": ("サマー香水", "暖かい季節にぴったりの軽やかでフレッシュなサマー香水。"),
        "ko": ("여름 향수", "따뜻한 날씨에 어울리는 가볍고 상쾌한 여름 향수."),
        "zh": ("夏季香水", "探索适合温暖天气的清新夏季香水。"),
        "ar": ("عطور صيفية", "اكتشف عطوراً صيفية منعشة بنوتات خفيفة وعليلة."),
        "hi": ("गर्मियों का इत्र", "गर्म मौसम के लिए हल्के, ताज़ा ग्रीष्मकालीन इत्र।"),
    },
    "winter": {
        "fr": ("Parfums d'Hiver", "Des fragrances chaudes et enveloppantes aux notes riches pour les jours froids."),
        "de": ("Winterparfums", "Warme und gemütliche Winterdüfte mit reichen, umhüllenden Noten."),
        "es": ("Perfumes de Invierno", "Fragancias cálidas y envolventes con notas ricas para los días fríos."),
        "it": ("Profumi Invernali", "Fragranze calde e avvolgenti con note ricche per i giorni freddi."),
        "pt": ("Perfumes de Inverno", "Fragrâncias quentes e envolventes com notas ricas para os dias frios."),
        "nl": ("Winterparfums", "Warme en gezellige wintergeuren met rijke, omhullende noten."),
        "pl": ("Perfumy Zimowe", "Ciepłe i przytulne zimowe zapachy z bogatymi, otulającymi nutami."),
        "tr": ("Kış Parfümleri", "Soğuk günler için zengin, saran notalarla sıcak kış kokuları."),
        "ja": ("ウィンター香水", "寒い日のための温かみのある豊かなウィンター香水。"),
        "ko": ("겨울 향수", "추운 날을 위한 따뜻하고 풍부한 겨울 향수."),
        "zh": ("冬季香水", "探索适合寒冷天气的温暖浓郁冬季香水。"),
        "ar": ("عطور شتوية", "اكتشف عطوراً شتوية دافئة بنوتات غنية للأيام الباردة."),
        "hi": ("सर्दियों का इत्र", "ठंडे दिनों के लिए गर्म और समृद्ध सर्दियों के इत्र।"),
    },
    "wedding": {
        "fr": ("Parfums de Mariage", "Trouvez le parfum idéal pour votre grand jour, des senteurs élégantes et mémorables."),
        "de": ("Hochzeitsparfums", "Finden Sie den perfekten Duft für Ihren besonderen Tag."),
        "es": ("Perfumes de Boda", "Encuentra la fragancia perfecta para tu día especial."),
        "it": ("Profumi da Matrimonio", "Trova la fragranza perfetta per il tuo giorno speciale."),
        "pt": ("Perfumes para Casamento", "Encontre a fragrância perfeita para o seu dia especial."),
        "nl": ("Bruiloftsparfums", "Vind het perfecte parfum voor uw bijzondere dag."),
        "pl": ("Perfumy Ślubne", "Znajdź idealny zapach na swój wyjątkowy dzień."),
        "tr": ("Düğün Parfümleri", "Özel gününüz için mükemmel kokuyu bulun."),
        "ja": ("ウェディング香水", "特別な日のための完璧なウェディング香水。"),
        "ko": ("웨딩 향수", "특별한 날을 위한 완벽한 웨딩 향수."),
        "zh": ("婚礼香水", "为您的特殊日子找到完美的婚礼香水。"),
        "ar": ("عطور الزفاف", "اعثر على العطر المثالي ليومك الخاص."),
        "hi": ("शादी का इत्र", "अपने खास दिन के लिए सही इत्र खोजें।"),
    },
    "sport": {
        "fr": ("Parfums Sport", "Des fragrances énergisantes qui vous gardent frais pendant l'effort."),
        "de": ("Sport-Parfums", "Belebende Sportdüfte, die Sie bei aktiven Aktivitäten frisch halten."),
        "es": ("Perfumes Deportivos", "Fragancias energizantes que te mantienen fresco durante la actividad."),
        "it": ("Profumi Sportivi", "Fragranze energizzanti che ti mantengono fresco durante l'attività."),
        "pt": ("Perfumes Esportivos", "Fragrâncias energizantes que mantêm você fresco durante atividades."),
        "nl": ("Sportparfums", "Energieke sportgeuren die u fris houden tijdens activiteiten."),
        "pl": ("Perfumy Sportowe", "Energetyzujące zapachy sportowe na aktywne dni."),
        "tr": ("Spor Parfümleri", "Aktif yaşam için canlandırıcı spor kokuları."),
        "ja": ("スポーツ香水", "アクティブな時間をフレッシュに保つスポーツ香水。"),
        "ko": ("스포츠 향수", "활동적인 시간을 상쾌하게 유지하는 스포츠 향수."),
        "zh": ("运动香水", "运动时保持清新的活力运动香水。"),
        "ar": ("عطور رياضية", "عطور منشطة تبقيك منتعشاً أثناء النشاط."),
        "hi": ("स्पोर्ट इत्र", "सक्रिय गतिविधियों के दौरान ताज़ा रखने वाले ऊर्जावान स्पोर्ट इत्र।"),
    },
    "travel": {
        "fr": ("Parfums de Voyage", "Des fragrances pratiques et adaptées aux voyageurs et aventuriers."),
        "de": ("Reiseparfums", "Reisefreundliche Düfte für Abenteurer und Weltenbummler."),
        "es": ("Perfumes de Viaje", "Fragancias prácticas para viajeros y aventureros."),
        "it": ("Profumi da Viaggio", "Fragranze pratiche per viaggiatori e avventurieri."),
        "pt": ("Perfumes de Viagem", "Fragrâncias práticas para viajantes e aventureiros."),
        "nl": ("Reisparfums", "Reisvriendelijke geuren voor avonturiers en globetrotters."),
        "pl": ("Perfumy Podróżne", "Praktyczne zapachy podróżne dla podróżników i odkrywców."),
        "tr": ("Seyahat Parfümleri", "Maceracılar ve gezginler için seyahat parfümleri."),
        "ja": ("トラベル香水", "冒険家や旅行者のためのトラベル香水。"),
        "ko": ("트래블 향수", "모험가와 여행자를 위한 트래블 향수."),
        "zh": ("旅行香水", "适合冒险家和旅行者的旅行香水。"),
        "ar": ("عطور السفر", "عطور عملية للمسافرين والمغامرين."),
        "hi": ("ट्रैवल इत्र", "साहसिक यात्रियों के लिए व्यावहारिक ट्रैवल इत्र।"),
    },
}

# === SUBFAMILY: Use English with lang prefix for now (will be enriched via API later) ===
# Subfamily titles translated per lang
SUBFAMILY_TITLES = {
    "fr": {
        "floral-fruity": "Parfums Floraux Fruités", "floral-white": "Parfums Floraux Blancs",
        "floral-powdery": "Parfums Floraux Poudrés", "floral-green": "Parfums Floraux Verts",
        "floral-aldehyde": "Parfums Floraux Aldéhydés", "floral-aquatic": "Parfums Floraux Aquatiques",
        "oriental-spicy": "Parfums Orientaux Épicés", "oriental-vanilla": "Parfums Orientaux Vanillés",
        "oriental-amber": "Parfums Orientaux Ambrés", "oriental-woody": "Parfums Orientaux Boisés",
        "oriental-floral": "Parfums Orientaux Floraux",
        "woody-aromatic": "Parfums Boisés Aromatiques", "woody-spicy": "Parfums Boisés Épicés",
        "woody-dry": "Parfums Boisés Secs", "woody-mossy": "Parfums Boisés Moussus",
        "woody-earthy": "Parfums Boisés Terreux",
        "fresh-citrus": "Parfums Agrumes", "fresh-aquatic": "Parfums Aquatiques",
        "fresh-green": "Parfums Verts", "fresh-ozonic": "Parfums Ozoniques",
        "fresh-fruity": "Parfums Frais Fruités",
        "aromatic-fougere": "Parfums Fougère", "aromatic-herbal": "Parfums aux Herbes",
        "aromatic-spicy": "Parfums Aromatiques Épicés", "aromatic-marine": "Parfums Marins",
        "chypre-fruity": "Parfums Chyprés Fruités", "chypre-floral": "Parfums Chyprés Floraux",
        "chypre-leather": "Parfums Chyprés Cuirés", "chypre-green": "Parfums Chyprés Verts",
        "gourmand-vanilla": "Parfums Gourmands Vanillés", "gourmand-sweet": "Parfums Sucrés",
        "gourmand-coffee": "Parfums Café", "gourmand-chocolate": "Parfums Chocolat",
    },
}

# For non-FR languages, we'll use a simpler approach
def get_subfamily_title(lang, slug):
    if lang in SUBFAMILY_TITLES and slug in SUBFAMILY_TITLES[lang]:
        return SUBFAMILY_TITLES[lang][slug]
    # Fallback: read from EN file
    en_path = f"/home/ubuntu/hbb/content/en/perfumes/{slug}/_index.md"
    if os.path.exists(en_path):
        with open(en_path) as f:
            for line in f:
                if line.startswith('title:'):
                    return line.split('"')[1]
    return slug.replace("-", " ").title() + " Perfumes"

def get_subfamily_desc(lang, slug):
    # Read from EN file
    en_path = f"/home/ubuntu/hbb/content/en/perfumes/{slug}/_index.md"
    if os.path.exists(en_path):
        with open(en_path) as f:
            for line in f:
                if line.startswith('description:'):
                    return line.split('"')[1]
    return ""

# Read EN subcategories to get the full list
EN_BASE = "/home/ubuntu/hbb/content/en/perfumes"
en_subcats = []
for d in sorted(os.listdir(EN_BASE)):
    idx = os.path.join(EN_BASE, d, "_index.md")
    if os.path.isdir(os.path.join(EN_BASE, d)) and os.path.exists(idx):
        # Parse frontmatter
        meta = {}
        with open(idx) as f:
            in_front = False
            for line in f:
                line = line.strip()
                if line == "---":
                    if in_front:
                        break
                    in_front = True
                    continue
                if in_front and ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip()] = val.strip().strip('"')
        en_subcats.append((d, meta))

print(f"Found {len(en_subcats)} EN subcategories")

# Generate for each language
LANGS = ["fr", "de", "es", "it", "pt", "nl", "pl", "tr", "ja", "ko", "zh", "ar", "hi"]
total = 0

for lang in LANGS:
    section_dir = SECTION_DIRS[lang]
    base = f"/home/ubuntu/hbb/content/{lang}/{section_dir}"
    count = 0
    
    for slug, meta in en_subcats:
        stype = meta.get("subcategory_type", "")
        svalue = meta.get("subcategory_value", "")
        emoji = meta.get("emoji", "✨")
        
        # Get translated title and description
        if stype == "gender" and slug in GENDER:
            title, desc = GENDER[slug].get(lang, (meta.get("title", ""), meta.get("description", "")))
        elif stype == "family" and slug in FAMILY:
            title, desc = FAMILY[slug].get(lang, (meta.get("title", ""), meta.get("description", "")))
        elif stype == "occasion" and slug in OCCASION:
            title, desc = OCCASION[slug].get(lang, (meta.get("title", ""), meta.get("description", "")))
        elif stype == "subfamily":
            title = get_subfamily_title(lang, slug)
            desc = get_subfamily_desc(lang, slug)
        else:
            title = meta.get("title", slug)
            desc = meta.get("description", "")
        
        # Create directory and file
        dir_path = os.path.join(base, slug)
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, "_index.md")
        with open(file_path, "w") as f:
            f.write("---\n")
            f.write(f'title: "{title}"\n')
            f.write(f'description: "{desc}"\n')
            f.write(f'emoji: "{emoji}"\n')
            f.write(f'subcategory_type: "{stype}"\n')
            f.write(f'subcategory_value: "{svalue}"\n')
            f.write("---\n")
        
        count += 1
    
    print(f"  {lang}: {count} subcategories created in content/{lang}/{section_dir}/")
    total += count

print(f"\nTOTAL: {total} files created across {len(LANGS)} languages")
