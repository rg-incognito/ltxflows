"""
Prompt Engine — Hindi/Hinglish facts + LTX-Video motion prompts.
Everything is in Hinglish for maximum engagement with Indian audience.
"""

import random

# (fact_screen, hook, tts_text ~55 words Hinglish — punchy, dramatic, viral)
FACTS = {
    "liquid": [
        (
            "Shahad 3000 saal baad bhi fresh rehta hai — Egyptian tombs mein mila aur scientists ne khaya!",
            "3000 saal purana khana khaya scientists ne — aur wo theek rahe!",
            "Ruko ek second. Scientists ne Egyptian pyramid se 3000 saal purana shahad nikala — aur chakh ke dekha. Bilkul fresh tha. Kharab nahi hua tha. Ek bhi bacteria nahi bacha tha andar. Kyunki shahad mein itna sugar hai ki koi bhi microbe ek minute bhi nahi jeeta. Yeh nature ka immortal food hai. Ghar mein rakha shahad? Wo bhi kabhi expire nahi hoga — kabhi nahi!"
        ),
        (
            "Paani ek saath barf bhi, liquid bhi, aur bhaap bhi hota hai — EK HI WAQT MEIN!",
            "Ek cheez jo ek saath teen jagah hoti hai — yeh magic nahi, science hai!",
            "Yeh sunke believe nahi hoga. Paani — sirf paani — ek hi waqt mein solid, liquid, aur gas teen forms mein exist kar sakta hai. Isko Triple Point kehte hain. Ek specific temperature, ek specific pressure — aur paani teeno phases mein ek saath aa jaata hai. Scientists ne lab mein apni aankhon se dekha hai. Agar yeh real nahi lagta — Google karo Triple Point of water. Mind blown guarantee hai!"
        ),
        (
            "200 tonne ka jahaz paani mein isliye tairta hai — kyunki shape hi sab kuch hai!",
            "Loha doobta hai — toh jahaz kyun nahi? Answer sunke reh jaoge!",
            "Ek sawaal jo school mein kisi ne jawab nahi diya. Loha paani mein doob jaata hai. Toh 200,000 tonne ka jahaz kyun nahi doobta? Kyunki jahaz ki shape itni hoti hai ki wo apne weight se zyada paani hatata hai bahar. Yeh Archimedes principle hai — 2200 saal purana! Aur pata hai usne yeh kab discover kiya? Nahaate waqt. Nanga ghoom gaya tha khushi mein. Science is wild!"
        ),
    ],
    "sand": [
        (
            "Sirf Earth ke beaches ki ret ke daane — Poore Universe ke taaron se zyada hain!",
            "Ret ke daane stars se zyada? Yeh number sunke dimag ghoom jayega!",
            "Ek second ke liye ruko. Duniya ke saare beaches ki ret ke daane count karo — 7.5 quintillion grains hain. Ab poore Universe mein stars count karo — wo kam hain! Haan. Earth ke ek planet ki ret — pure Universe ke stars se zyada. Yeh number itna bada hai ki human brain samajh hi nahi sakta. Hum ek choti si ret ki duniya mein kitni badi soch lete hain apni."
        ),
        (
            "Quicksand mein poora dub nahi sakte — Hollywood ne 50 saal jhooth bolaya!",
            "Quicksand ka sach — yeh movie ka sabse bada jhooth tha!",
            "Hollywood movies mein jo quicksand dekha — bilkul fake tha. Human body quicksand se halki hoti hai — poora dub nahi sakte. Waist tak jaoge maximum. Aur nikalna? Slow slow movements karo, peeche jhuko, ek ek pair dhire se nikalo. Panic mat karo. Yeh life-saving information hai jo kisi ne nahi bataya. Ek share se kisi ki jaan bach sakti hai — sach mein."
        ),
        (
            "Kuch deserts mein ret ke teelay khud gaana gaate hain — Scientists ne record kiya!",
            "Ret gaana gaati hai — desert mein actual music aata hai, sach mein!",
            "Yeh jaadu nahi hai. Morocco, China aur California ke deserts mein ret ke dune actual sound produce karte hain — ek deep booming music, jaise bass guitar baj raha ho. Hawa chalti hai, ret ke daane ek specific tarike se vibrate karte hain, aur music nikalta hai. Scientists ne microphones se record kiya hai. Nature itna beautiful artist hai ki hum sirf sochte reh jaate hain — kya yeh real hai?"
        ),
    ],
    "geometric": [
        (
            "Madhumakkhi ne hexagon choose kiya — koi bhi aur shape 8% zyada wax waste karti!",
            "Bees ne wo solve kiya jo mathematicians ne sadiyon mein solve kiya!",
            "Kisi ne bees ko engineering nahi sikhaya. Phir bhi unhone wo shape choose ki jo mathematically sabse perfect hai — hexagon. Circles use karte toh gaps rehte. Squares use karte toh 8% zyada wax lagti. Sirf hexagon mein zero waste, maximum storage. Aur bees yeh 30 million saal se kar rahi hain — jab humans ka koi naama nishaan nahi tha. Nature ka IQ humse bahut zyada hai."
        ),
        (
            "1,1,2,3,5,8 — Yeh sequence sunflower mein hai, galaxies mein hai, tumhare chehere mein bhi hai!",
            "Universe ka ek secret code hai — aur wo hamesha se tumhare saamne tha!",
            "Fibonacci sequence — 1, 1, 2, 3, 5, 8, 13. Har number pichle do ka sum. Simple lagta hai na? Ab sunno — yeh pattern sunflower ke seeds mein hai. Nautilus shell mein hai. Pine cone mein hai. Aur Milky Way galaxy ke spiral arms mein bhi. Kisi ne design nahi kiya — nature khud is code ko repeat karti rehti hai. Humara chehra bhi isi ratio mein hota hai. We are the universe."
        ),
        (
            "Abhi tak do bhi same snowflakes nahi mile — har ek crystal is duniya mein unique hai!",
            "Duniya mein koi bhi do snowflakes same nahi — exactly tumhari tarah!",
            "Har snowflake ek ek alag hota hai. Ek bhi same nahi. Kyunki baraf ka crystal bante waqt temperature, humidity, pressure — har microsecond alag hota hai. Possible combinations itne hain ki same snowflake banana mathematically almost impossible hai. Yeh zaroor socho — billions of snowflakes girte hain, aur ek bhi same nahi. Aur tum bhi is duniya mein exactly ek ho. Koi doosra tum nahi ho. Kabhi nahi tha."
        ),
    ],
    "food": [
        (
            "Strawberry berry nahi hai — lekin banana, avocado aur watermelon berry hain!",
            "Strawberry berry nahi? Science ne saari life ka jhooth pakad liya!",
            "School mein jo padha tha — bhool jao. Botanical science mein berry ki definition hai — single flower se bane, seeds andar hon. Strawberry ke seeds bahar hote hain — berry nahi hai. Lekin banana? Berry hai. Avocado? Berry hai. Watermelon? Bhi berry hai. Tomato bhi. Yeh science ka official classification hai, koi joke nahi. Kitni cheezon ke naam hi galat hain — yeh toh bas shuruat hai."
        ),
        (
            "Aztecs mein chocolate paisa tha — ek turkey sirf 100 cacao beans mein milti thi!",
            "Chocolate paisa tha ek zamane mein — aur log gold se zyada isko chahte the!",
            "Ek waqt tha jab chocolate khaate nahi the — kharchte the. Aztec empire mein cacao beans actual currency tha. Ek turkey 100 beans mein milti thi. Spanish log Mexico aaye, gold dhoondha — lekin locals zyada cacao chahte the. Aaj chocolate trillion dollar industry hai. Ek simple seed jo currency bana, phir luxury bana, phir addiction bana. Kya pata kal kaunsi cheez aisi ho jaaye — crypto ki tarah?"
        ),
        (
            "Gajar pehle purple hoti thi — Dutch ne sirf apne king ko impress karne ke liye orange banaya!",
            "Orange gajar sirf 400 saal purani invention hai — pehle purple thi!",
            "Jo orange gajar aaj normal lagti hai — woh ek political decision tha. Original gajar purple, white, yellow hoti thi. Dutch farmers ne 17th century mein orange gajar selectively breed ki — apne ruler William of Orange ko tribute dene ke liye. Ek royal colour jo ab duniya bhar ke kitchens mein hai. Ek farmer ka political gesture — aur aaj hum sochte hain gajar toh orange hi hoti hai. History kitni sly hai."
        ),
    ],
    "metal": [
        (
            "Gallium metal haath mein rakhte hi pighal jaata hai — aur yeh bilkul safe hai!",
            "Haath ki garmi se pighal jaane wala metal exist karta hai — dekho toh sahi!",
            "Ek metal hai jo haath mein rakhte hi pighal jaata hai — literally. Gallium ka melting point sirf 29.8 degree hai. Tumhara body temperature 37 degree hai. Haath mein rakhte hi liquid ban jaata hai. Solid tha — ek second mein liquid. Aur toxic nahi hai, safe hai. Scientists is par liquid metal robots ke experiments kar rahe hain. Terminator wali technology actually develop ho rahi hai — right now."
        ),
        (
            "Poori history ka saara gold sirf saade teen Olympic pools mein samayega — itna rare hai!",
            "Saari duniya ka gold — sirf 3 pools bhar — aur hum iske liye wars ladte hain!",
            "Poori human history mein jo gold mina gaya — sab ek jagah rakho — sirf saade teen Olympic swimming pools fill honge. Bas. Itna kam. Itna rare. Aur interesting baat — wo gold actually asteroids se aaya hai Earth par. Earth ke core mein aur bhi hai — lekin itna deep hai ki kabhi nahi nikal sakte. Itni rare cheez ke liye wars hue, empires gire. Yeh perspective bahut kuch bol deta hai humari priorities ke baare mein."
        ),
        (
            "Aerogel 99.8% sirf hawa hai — phir bhi blowtorch ki aag rok leta hai!",
            "Dhuan lagta hai — solid hai — aag rok leta hai — yeh Aerogel hai!",
            "Dekho toh dhuan lagta hai. Chuo toh solid nikle. Aur blowtorch ki seedhi aag ke neeche rakh do — dusri taraf phool nahi jalayta. Yeh Aerogel hai. 99.8 percent sirf air, baaki silica. Ek kilo se ek football field cover ho sakta hai. NASA iska use karta hai Mars rovers mein. Future mein space suits mein hoga. Yeh material lagbhag kisi superhero movie se liya hua lagta hai — lekin real hai, ekdum real."
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
