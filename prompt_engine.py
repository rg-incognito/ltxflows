"""
Prompt Engine — Hindi/Hinglish facts + LTX-Video motion prompts.
Everything is in Hinglish for maximum engagement with Indian audience.
"""

import random

# (fact_screen, hook, tts_text ~60 words Hinglish)
FACTS = {
    "liquid": [
        (
            "Shahad kabhi kharab nahi hota — 3000 saal purana bhi kha sakte ho!",
            "3000 saal purana shahad — aaj bhi fresh!",
            "Yaar suno, shahad kabhi expire nahi hota. Egyptian tombs mein 3000 saal purana shahad mila aur scientists ne taste kiya — bilkul fresh tha! Kyun? Kyunki shahad mein itna sugar hota hai aur itni kam paani ki koi bhi bacteria survive nahi kar sakta. Nature ka sabse perfect preservative. Aaj jo shahad kharida, wo hazaaron saal baad bhi kha sakte hain. Nature is truly incredible. Share karo yaar!"
        ),
        (
            "Paani ek saath solid, liquid aur gas — Teen phases ek saath possible hai!",
            "Paani ka triple point — science ka sabse bada magic!",
            "Yeh sunke dimag ghoom jayega. Paani ek hi waqt mein barf bhi ban sakta hai, paani bhi reh sakta hai, aur bhaap bhi — ek saath teeno! Isko Triple Point kehte hain. Sirf 0.01 degree Celsius aur 611 Pascal pressure par yeh possible hai. Scientists ne lab mein yeh achieve kiya hai. Physics itni wild hai bhai. Aisa kuch nature mein bhi hota hai. Comment mein batao — kya yeh believe karte ho?"
        ),
        (
            "Samundar ka paani itna bhari hai ki usme steel bhi tair sakta hai!",
            "Steel ka jahaj paani mein kyun dubta nahi? Science sunoge?",
            "Aik sawaal — loha paani mein doob jaata hai toh itna bada jahaz kaise tairta hai? Kyunki jahaz ki shape aisi hoti hai ki wo apne weight se zyada paani hatata hai. Archimedes principle! 3000 saal pehle ek Greek scientist ne nahaate waqt yeh discover kiya aur 'Eureka' chillaya. Woh nanga bahar bhaag gaya khushi mein. Science ka sabse funny discovery moment. Like karo yaar!"
        ),
    ],
    "sand": [
        (
            "Dharti ke beaches ki ret ke daane — Universe ke taaron se bhi zyada hain!",
            "Ret ke daane ya tare — kaunse zyada hain? Answer sunoge?",
            "Ek kaam karo — imagine karo duniya ke saare beaches ka har ek ret ka daana count karo. That is 7.5 quintillion grains. Ab suno — Universe mein itne bhi tare nahi hain! Haan, Universe mein stars se zyada ret ke daane hain sirf Earth ke beaches par. Yeh number itna bada hai ki human brain process hi nahi kar sakta. Hum kitne chote hain is universe mein. Comment mein batao — kaisa feel hua?"
        ),
        (
            "Quicksand mein poora dub nahi sakte — Movies ne jhooth bola hai!",
            "Quicksand ka sach — Hollywood ka sabse bada jhooth!",
            "Hollywood ne humein baar baar bewaqoof banaya hai. Quicksand mein poora dub nahi sakte — kyunki human body quicksand se kam dense hoti hai. Maximum waist tak phase sakte ho. Lekin problem yeh hai ki nikalna bahut mushkil hota hai. Slow movements karo, peeche jhuko, aur धीरे धीरे pair nikalo. Movies mein jo dikhate hain woh complete fiction hai. Yeh life-saving information hai — share karo!"
        ),
        (
            "Kuch deserts mein ret ke dune gaana gaate hain — Yeh sach hai!",
            "Singing dunes — ret ka sangeet sunna chahoge?",
            "Yeh bahut magical lagega lekin yeh sach hai. Morocco, China aur California ke kuch deserts mein ret ke dune actual music produce karte hain. Hawa chalti hai toh ret ke daane vibrate karte hain aur ek deep booming awaaz aati hai — bilkul jaise koi bass guitar baja raha ho. Scientists ne discover kiya ki specific grain size aur shape yeh sound create karta hai. Nature khud ek musician hai bhai. Follow karo roz aisi facts ke liye!"
        ),
    ],
    "geometric": [
        (
            "Honeycomb ka hexagon — Nature ka sabse perfect engineering hai!",
            "Bees engineers hain — Hexagon proof hai!",
            "Bees ko kisi engineering college nahi bheja lekin unhone nature ka most efficient shape discover kiya — Hexagon. Is shape mein minimum wax lagti hai aur maximum honey store hoti hai. Agar circles use karte toh 8 percent zyada wax lagti. Agar squares use karte toh gaps rehte. Sirf hexagon perfect hai — mathematically proven. 30 million saal pehle bees ne yeh solve kiya jab humans exist hi nahi karte the. Genius insects hain bhai!"
        ),
        (
            "Fibonacci sequence — 1,1,2,3,5,8 — Yeh Universe ka secret code hai!",
            "Universe ka ek hi code hai — aur wo bahut simple hai!",
            "Fibonacci sequence sunno — 1, 1, 2, 3, 5, 8, 13, 21 — har number pichle do ka sum. Ab yeh crazy hai — yeh sequence sunflower ke seeds mein hoti hai, nautilus shell ke spiral mein, banana ke sections mein, pine cone mein, aur galaxy ke arms mein bhi! Nature baar baar yahi pattern use karti hai kyunki yeh mathematically most efficient growth pattern hai. Koi designer nahi, sirf pure mathematics. Universe ek mathematical poem hai bhai!"
        ),
        (
            "Snowflake ka har crystal alag hota hai — 2 snowflakes kabhi same nahi!",
            "Duniya mein koi bhi 2 snowflakes same nahi hote — ye sach hai!",
            "Is duniya mein abhi tak ek bhi aisa snowflake nahi mila jo dusre se bilkul same ho. Har ek crystal alag hota hai. Kyun? Kyunki baraf ka crystal banate waqt hazaaron steps hote hain — temperature, humidity, pressure — har step slightly alag hota hai. Mathematically possible combinations itne hain ki same snowflake banana practically impossible hai. Is duniya mein aap bhi unique ho exactly isi tarah. Deep hai na? Share karo!"
        ),
    ],
    "food": [
        (
            "Strawberry technically berry nahi hai — Banana aur Avocado berry hain!",
            "Strawberry berry nahi? Science ne sabki knowledge tod di!",
            "Botanical definition sunoge toh dimag ghoom jayega. Strawberry technically berry nahi hai — yeh actually ek accessory fruit hai. Lekin botanically — banana ek berry hai. Avocado ek berry hai. Watermelon bhi ek berry hai. Aur tomato bhi! Berry ki definition hai ki single flower se develop ho aur seeds andar hon. Strawberry ke seeds bahar hote hain — isliye berry nahi. Science ne humari saari childhood knowledge tod di. Comment mein batao kya soch rahe ho!"
        ),
        (
            "Chocolate Aztecs ki currency thi — Gold se bhi zyada valuable!",
            "Chocolate paisa tha ek zamane mein — Aztecs ka secret!",
            "Ek zamane mein chocolate khaana nahi — paisa tha. Aztec civilization mein cacao beans currency ke roop mein use hote the. Ek turkey sirf 100 cacao beans mein milta tha. Spanish explorers jab Mexico aaye, unhone gold dhundha — lekin locals cacao ko zyada valuable samajhte the. Aaj chocolate ek trillion dollar industry hai. Sochna hai — aaj ki kaunsi cheez future mein currency ban sakti hai? Interesting thought hai na! Comment karo!"
        ),
        (
            "Gajar pehle purple thi — Dutch ne orange colour 17th century mein banaya!",
            "Orange gajar sirf 400 saal purani hai — pehle purple thi!",
            "Aaj hum jis orange gajar ko normal samajhte hain — woh actually 17th century ki invention hai. Original wild carrots purple, white, aur yellow hoti thin. Dutch farmers ne orange gajar selectively breed ki — apne ruler William of Orange ko tribute dene ke liye. Orange unka royal color tha. Ek political statement jo ab duniya bhar mein spread ho gaya. Hum sochte hain gajar toh hamesha se orange thi. History kitni interesting hai yaar! Share karo!"
        ),
    ],
    "metal": [
        (
            "Gallium haath mein rakhne se pighal jaata hai — Yeh real metal hai!",
            "Haath mein dharo toh pighal jayega — yeh metal hai bhai!",
            "Gallium dekha hai kabhi? Yeh ek metal hai jo almost solid rehta hai — lekin haath mein pakdo toh pighal jaata hai. Melting point sirf 29.8 degree Celsius hai — human body temperature 37 degree hai. Isliye literally haath mein rakhne se liquid ban jaata hai. Aur cool part — yeh non-toxic hai, safe hai touch karne ke liye. Scientists isko liquid metal robots ke liye study kar rahe hain. Terminator real ho sakta hai future mein! Mind-blowing hai na!"
        ),
        (
            "Duniya ka saara gold sirf saade teen Olympic pools mein samayega!",
            "Duniya ka saara gold — sirf 3 swimming pools bhar — itna rare hai!",
            "Perspective changing fact suno. Humans ne history mein total 197,000 tonnes gold mine kiya hai. Itna saara gold agar ek jagah rakho toh sirf saade teen Olympic swimming pools fill honge. Itna rare hai gold. Aur interesting baat — zyaada gold actually asteroids se aaya hai. Earth ke core mein aur bhi gold hai — lekin itna deep hai ki kabhi nahi nikal sakte. Aur phir bhi hum iske liye wars ladte hain. Perspective amazing hai na bhai!"
        ),
        (
            "Aerogel 99.8% sirf hawa hai — Phir bhi solid material hai yeh!",
            "Dekho toh smoke lagti hai — chuo toh solid nikle — Aerogel!",
            "NASA ka favourite material sunna chahoge? Aerogel — dekh ke lagta hai dhuan hai, lekin touch karo toh solid hai. 99.8 percent air aur sirf 0.2 percent silica. Ek kilogram aerogel ek football field jaisi area cover kar sakta hai. Itna insulating hai ki blowtorch ke neeche ek phool rakh do aerogel ke through — phool nahi jalayi. Mars rovers mein yeh use hota hai. Scientists isse future space suits mein use karna chahte hain. Future is here yaar!"
        ),
    ],
}

NICHES = list(FACTS.keys())

# English prompts for Pollinations image generation (FLUX works best in English)
IMAGE_PROMPTS = {
    "liquid": [
        "extreme close-up macro shot of thick golden honey slowly dripping from a silver spoon, soft warm backlight, photorealistic, 4K, ultra detailed, black background",
        "slow motion pour of deep red liquid into crystal glass, surface tension visible, dark dramatic studio lighting, macro lens, cinematic 4K",
        "extreme close-up overhead view of blue ink slowly spreading in clear water, dark background, high contrast, macro lens, 4K",
        "thick caramel sauce slowly flowing over a golden surface, warm amber tones, soft diffused studio light, photorealistic macro 4K",
    ],
    "sand": [
        "close-up macro shot of fine white sand particles slowly falling like a waterfall curtain, warm golden backlight creating sparkle, dark background, 4K",
        "overhead view of multicolored sand being poured in circular patterns, vibrant reds blues yellows, studio lighting, ultra detailed 4K",
        "extreme macro of black sand falling through a glass hourglass, warm golden backlight, crisp detail, cinematic 4K",
        "close-up of desert sand dune ripples with dramatic raking light, golden hour, sharp shadows, ultra-detailed photorealistic",
    ],
    "geometric": [
        "perfect glossy marble sphere slowly rotating in studio, iridescent blue and gold surface, dark background, photorealistic 4K",
        "extreme close-up of intricate Islamic geometric tile pattern, deep royal blue and gold leaf, perfectly symmetrical, macro lens 4K",
        "overhead view of perfect kaleidoscope pattern made from rose petals and water droplets, symmetrical, vibrant colors, studio lighting",
        "macro shot of a single snowflake crystal showing perfect hexagonal geometry, isolated on black velvet, ultra sharp, 4K",
    ],
    "food": [
        "extreme close-up of dark chocolate being slowly poured over fresh strawberries, thick glossy stream, soft bokeh background, photorealistic 4K",
        "macro shot of fresh honeycomb cross-section, perfect golden hexagonal cells filled with honey, warm glowing backlight, 4K",
        "slow pour of bright orange mango pulp, thick and glossy, tropical aesthetic, soft studio lighting, macro lens 4K",
        "close-up of molten caramel threads being pulled apart, amber colored, dark dramatic background, ultra detailed",
    ],
    "metal": [
        "extreme macro of molten gold being slowly poured into a mold, glowing liquid metal, dark dramatic studio lighting, photorealistic 4K",
        "close-up of liquid gallium metal morphing and flowing, mirror-like surface, dark studio background, ultra detailed 4K",
        "macro shot of intricate silver watch gears and jewel bearings, sharp depth of field, dark background, photorealistic",
        "overhead of chrome steel ball bearing dropping in extreme slow motion into mercury, ripple effect, high contrast studio",
    ],
}

# LTX-Video motion prompts (English, describe smooth cinematic motion)
LTX_PROMPTS = {
    "liquid": [
        "thick golden honey dripping slowly in extreme slow motion, smooth fluid dynamics, cinematic macro, soft warm lighting",
        "liquid flowing gracefully in slow motion, surface ripples expanding gently, cinematic depth of field, ambient studio light",
        "fluid ink diffusing slowly in water, soft tendrils spreading, peaceful slow motion, macro cinematic shot",
        "viscous caramel flowing and stretching in ultra slow motion, warm amber glow, smooth fluid motion",
    ],
    "sand": [
        "fine sand grains cascading slowly like a waterfall, each grain catching light, ultra slow motion macro, peaceful ASMR",
        "sand pouring and spreading in circular patterns, slow rotation, ambient studio lighting, satisfying ASMR motion",
        "sand falling through hourglass in slow motion, golden particles catching light, peaceful meditative motion",
        "wind gently moving sand dune surface, ripple patterns forming slowly, cinematic aerial perspective",
    ],
    "geometric": [
        "perfect sphere slowly rotating in studio light, iridescent surface shifting colors smoothly, elegant slow spin",
        "geometric tile pattern slowly zooming in revealing infinite detail, smooth camera movement, ambient light",
        "kaleidoscope of flower petals slowly rotating and morphing, smooth symmetrical motion, soft studio lighting",
        "snowflake crystal slowly rotating in place, catching light at different angles, peaceful slow motion",
    ],
    "food": [
        "dark chocolate pouring slowly in thick glossy stream, smooth flowing motion, soft cinematic lighting",
        "honey slowly dripping from honeycomb, thick golden drops forming in ultra slow motion, ASMR satisfying",
        "mango pulp slowly flowing and pooling, vibrant orange, smooth viscous motion, warm tropical lighting",
        "caramel threads slowly stretching and flowing, amber liquid catching warm light, ultra slow motion",
    ],
    "metal": [
        "molten gold slowly pouring in a glowing stream, liquid metal catching dramatic light, slow motion macro",
        "liquid gallium flowing and morphing like living mercury, mirror surface rippling, slow hypnotic motion",
        "watch gears slowly turning with precision, jewels gleaming, smooth mechanical motion, macro cinematic",
        "metal ball dropping into liquid in ultra slow motion, ripples expanding outward, high contrast dramatic light",
    ],
}

_TITLES_HI = {
    "liquid": [
        "शहद का जादू 🍯 | Satisfying ASMR #Shorts #Satisfying",
        "पानी की बूंदें ✨ | Mind-blowing Facts #Shorts",
        "तरल का जादू 💧 | Oddly Satisfying #Shorts",
    ],
    "sand": [
        "रेत का खेल 🏖️ | Satisfying Sand ASMR #Shorts",
        "रेत की दुनिया ✨ | Amazing Facts #Shorts",
        "बालू का जादू 🌅 | Satisfying Video #Shorts",
    ],
    "geometric": [
        "गणित का जादू 🔷 | Perfect Geometry #Shorts",
        "प्रकृति का कोड ✨ | Fibonacci Facts #Shorts",
        "ज्यामिति की दुनिया 🌀 | Mind-blowing #Shorts",
    ],
    "food": [
        "खाने का विज्ञान 🍓 | Food Facts #Shorts",
        "चॉकलेट का इतिहास 🍫 | Amazing Facts #Shorts",
        "खाने की दुनिया 🥑 | Satisfying #Shorts",
    ],
    "metal": [
        "धातु का जादू 🔥 | Satisfying Metal #Shorts",
        "सोने का रहस्य ⚙️ | Amazing Metal Facts #Shorts",
        "तरल धातु 🪙 | Oddly Satisfying #Shorts",
    ],
}


def generate_fact_and_subtitle(niche=None):
    """Returns (fact_screen, hook, subtitle, tts_text)."""
    if niche is None or niche not in FACTS:
        niche = random.choice(NICHES)
    fact_screen, hook, tts_text = random.choice(FACTS[niche])
    return fact_screen, hook, fact_screen, tts_text


def generate_prompt(niche=None):
    """Returns (image_prompt, ltx_motion_prompt, niche)."""
    if niche is None or niche not in IMAGE_PROMPTS:
        niche = random.choice(list(IMAGE_PROMPTS.keys()))
    idx = random.randrange(len(IMAGE_PROMPTS[niche]))
    return IMAGE_PROMPTS[niche][idx], LTX_PROMPTS[niche][idx], niche


def generate_title(niche=None):
    if niche not in _TITLES_HI:
        niche = random.choice(list(_TITLES_HI.keys()))
    return random.choice(_TITLES_HI[niche])
