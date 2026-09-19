import csv, random, re, os
from itertools import product

random.seed(42)

classes = [
"light_on","light_off","fan_on","fan_off","ac_on","ac_off","heater_on","heater_off",
"tv_on","tv_off","music_on","music_off","door_open","door_close","window_open","window_close",
"lock_door","unlock_door","alarm_on","alarm_off","temperature_up","temperature_down",
"temperature_status","humidity_status","lights_status","fans_status","ac_status","heater_status",
"tv_status","music_status","door_status","window_status","security_status","home_status",
"good_morning","good_night","welcome_home","leaving_home","sleep_mode","away_mode","movie_mode",
"party_mode","emergency"
]

# Hindi-first lexical alternatives. Device names remain where naturally used in Indian Roman Hindi.
lex = {
"light": ["batti","roshni","light"],
"fan": ["pankha","fan"],
"ac": ["AC","thandak wali machine","air conditioner"],
"heater": ["heater","garam hawa wali machine"],
"tv": ["TV","television","telivijan"],
"music": ["gaane","sangeet","dhun","musiq"],
"door": ["darwaza","dwaar"],
"window": ["khidki","jharokha"],
"lock": ["tala","kundee"],
"alarm": ["alarm","chetavni ghanti"],
"temperature": ["taapmaan","garmi ka star","tapman"],
"humidity": ["nami","hawa ki nami"],
"home": ["ghar","makaan"],
}

base = {
"light_on": ["{light} jala do","{light} chalu kar do","{light} on kar do","{light} ki roshni kar do","{light} roshan kar do"],
"light_off": ["{light} bujha do","{light} band kar do","{light} off kar do","{light} ki roshni hata do","{light} ko band kar dena"],
"fan_on": ["{fan} chala do","{fan} shuru kar do","{fan} on kar do","{fan} ghuma do","{fan} chalu kar do"],
"fan_off": ["{fan} band kar do","{fan} rok do","{fan} off kar do","{fan} ko chalaana band kar do"],
"ac_on": ["{ac} chala do","{ac} shuru kar do","{ac} on kar do","{ac} thandak chalu kar do","{ac} ko chala do"],
"ac_off": ["{ac} band kar do","{ac} rok do","{ac} off kar do","{ac} ki thandak band kar do"],
"heater_on": ["{heater} chala do","{heater} shuru kar do","{heater} on kar do","{heater} se garam hawa chala do"],
"heater_off": ["{heater} band kar do","{heater} rok do","{heater} off kar do","{heater} ki garmahat band kar do"],
"tv_on": ["{tv} chala do","{tv} shuru kar do","{tv} on kar do","{tv} laga do","{tv} khol do"],
"tv_off": ["{tv} band kar do","{tv} off kar do","{tv} ko rok do","{tv} hata do"],
"music_on": ["{music} chala do","{music} shuru kar do","{music} baja do","{music} laga do","{music} chalu kar do"],
"music_off": ["{music} band kar do","{music} rok do","{music} off kar do","{music} bajna band kar do"],
"door_open": ["{door} khol do","{door} khol dena","{door} ko khol do","{door} khula kar do"],
"door_close": ["{door} band kar do","{door} bhid do","{door} ko band kar do","{door} laga do"],
"window_open": ["{window} khol do","{window} khol dena","{window} ko khol do","{window} khuli kar do"],
"window_close": ["{window} band kar do","{window} bhid do","{window} ko band kar do","{window} laga do"],
"lock_door": ["{door} mein {lock} laga do","{door} par {lock} laga do","{door} ko {lock} kar do","{door} ko taale mein kar do"],
"unlock_door": ["{door} ka {lock} khol do","{door} se {lock} hata do","{door} ko {lock} se azaad kar do","{door} ka tala khol do"],
"alarm_on": ["{alarm} chalu kar do","{alarm} laga do","{alarm} on kar do","{alarm} sakriya kar do"],
"alarm_off": ["{alarm} band kar do","{alarm} hata do","{alarm} off kar do","{alarm} nishkriya kar do"],
"temperature_up": ["{temperature} badha do","{temperature} thoda upar kar do","kamre ki garmi badha do","taapmaan zyada kar do"],
"temperature_down": ["{temperature} ghata do","{temperature} thoda kam kar do","kamre ki garmi kam kar do","taapmaan neeche kar do"],
"temperature_status": ["kamre ka {temperature} batao","{temperature} kitna hai","abhi {temperature} kya hai","ghar ka taapmaan batao"],
"humidity_status": ["hawa mein {humidity} kitni hai","{humidity} ka star batao","abhi {humidity} batao","ghar ki hawa mein nami kitni hai"],
"lights_status": ["ghar ki {light} ka haal batao","kaunsi {light} jali hai batao","{light} ki sthiti batao","battiyon ka haal kya hai"],
"fans_status": ["ghar ke {fan} ka haal batao","kaunsa {fan} chal raha hai","{fan} ki sthiti batao","pankhon ka haal kya hai"],
"ac_status": ["{ac} ka haal batao","{ac} chal raha hai ya nahi","{ac} ki sthiti batao","thandak wali machine ki sthiti batao"],
"heater_status": ["{heater} ka haal batao","{heater} chal raha hai ya nahi","{heater} ki sthiti batao","garam hawa wali machine ka haal batao"],
"tv_status": ["{tv} ka haal batao","{tv} chal raha hai ya nahi","{tv} ki sthiti batao","television ki sthiti batao"],
"music_status": ["{music} chal rahe hain ya nahi","{music} ki sthiti batao","gaanon ka haal batao","sangeet chal raha hai kya"],
"door_status": ["{door} ki sthiti batao","kaunsa {door} khula hai","{door} band hai ya khula","darwazon ka haal batao"],
"window_status": ["{window} ki sthiti batao","kaunsi {window} khuli hai","{window} band hai ya khuli","khidkiyon ka haal batao"],
"security_status": ["ghar ki suraksha ka haal batao","suraksha ki sthiti kya hai","ghar surakshit hai ya nahi","suraksha vyavastha batao"],
"home_status": ["ghar ka haal batao","ghar ki poori sthiti batao","ghar mein sab theek hai kya","makaan ki vartaman sthiti batao"],
"good_morning": ["suprabhat","shubh prabhat","subah ho gayi","subah ki shubhkaamnaen"],
"good_night": ["shubh raatri","shubh raat","ab sone ka samay hai","raat ke liye sab band kar do"],
"welcome_home": ["main ghar aa gaya hoon","ghar wapas aa gaya","main laut aaya hoon","ghar pahunch gaya hoon"],
"leaving_home": ["main ghar se nikal raha hoon","ab main ghar ja raha hoon","main bahar ja raha hoon","ghar se ab nikalta hoon"],
"sleep_mode": ["sone ka mode laga do","sone ki vyavastha kar do","raat wala mode chalu kar do","ab sone ki taiyari kar do"],
"away_mode": ["ghar se bahar wala mode laga do","door rehne ka mode chalu kar do","main bahar hoon, bahar wala mode laga do","ghar ko anupasthiti mode mein kar do"],
"movie_mode": ["film dekhne ka mahaul bana do","cinema wala mode chalu kar do","film ka mode laga do","movie dekhne ki taiyari kar do"],
"party_mode": ["jashn wala mode chalu kar do","mehfil ka mahaul bana do","party ka mode laga do","jashn ka mahaul bana do"],
"emergency": ["aapatkaal hai","madad chahiye, aapatkaal hai","ghar mein aapat sthiti hai","yeh aapatkaal hai, turant dhyan do"]
}

# Context modifiers add semantic richness while keeping labels clear.
contexts = {
"light_on":["kamre mein","baithak mein","rasoi mein","upar wale kamre mein","andhere mein"],
"light_off":["kamre ki","baithak ki","rasoi ki","upar wale kamre ki","abhi jali hui"],
"fan_on":["kamre ka","baithak ka","rasoi ka","upar ka","mera kamre ka"],
"fan_off":["kamre ka","baithak ka","rasoi ka","upar ka","mera kamre ka"],
"ac_on":["kamre ka","baithak ka","upar wale kamre ka","sone wale kamre ka"],
"ac_off":["kamre ka","baithak ka","upar wale kamre ka","sone wale kamre ka"],
"heater_on":["kamre ka","baithak ka","upar wale kamre ka","thande kamre ka"],
"heater_off":["kamre ka","baithak ka","upar wale kamre ka","thande kamre ka"],
}

# Specific semantic paraphrase templates, with controlled small noise.
semantic = {
"light_on":["andhera ho raha hai, {light} jala do","kamra andhera hai, {light} roshan kar do","mujhe roshni chahiye, {light} chalu karo"],
"light_off":["ab roshni ki zarurat nahi, {light} bujha do","kamra khaali hai, {light} band kar do","roshni hata do, {light} band karo"],
"fan_on":["garmi lag rahi hai, {fan} chala do","hawa chahiye, {fan} shuru karo","kamre mein hawa chala do"],
"fan_off":["ab hawa nahi chahiye, {fan} band karo","thandak theek hai, {fan} rok do"],
"ac_on":["garmi zyada hai, {ac} chala do","kamra thanda karna hai, {ac} on karo"],
"ac_off":["ab kaafi thandak hai, {ac} band karo","kamra theek hai, {ac} rok do"],
"heater_on":["thand lag rahi hai, {heater} chala do","kamra garam karna hai, {heater} on karo"],
"heater_off":["ab garmi theek hai, {heater} band karo","kamra garam ho gaya, {heater} rok do"],
"tv_on":["kuch dekhna hai, {tv} chala do","samachar dekhne hain, {tv} on karo"],
"tv_off":["dekhna ho gaya, {tv} band karo","ab kuch nahi dekhna, {tv} off karo"],
"music_on":["mahaul shaant hai, {music} chala do","thoda sangeet sunna hai, {music} baja do"],
"music_off":["ab chupchaap rehna hai, {music} band karo","gaane sun liye, {music} rok do"],
"door_open":["andar aana hai, {door} khol do","bahar jaana hai, {door} khol do"],
"door_close":["andar aa gaye, {door} band kar do","hawa aa rahi hai, {door} bhid do"],
"window_open":["taazi hawa chahiye, {window} khol do","kamra ghutan wala hai, {window} khol do"],
"window_close":["bahar se hawa zyada aa rahi hai, {window} band karo","kamra thanda ho raha hai, {window} bhid do"],
"temperature_up":["thand lag rahi hai, {temperature} badha do","kamra thoda garam chahiye, taapmaan upar karo"],
"temperature_down":["garmi lag rahi hai, {temperature} ghata do","kamra thoda thanda chahiye, taapmaan kam karo"],
}

# Replace placeholders with randomized lexical variants.
placeholder_map = {
"light":lex["light"],"fan":lex["fan"],"ac":lex["ac"],"heater":lex["heater"],
"tv":lex["tv"],"music":lex["music"],"door":lex["door"],"window":lex["window"],
"lock":lex["lock"],"alarm":lex["alarm"],"temperature":lex["temperature"],"humidity":lex["humidity"]
}

def fill(t):
    for k, vals in placeholder_map.items():
        if "{"+k+"}" in t:
            t = t.replace("{"+k+"}", random.choice(vals))
    return t

# Small, non-destructive conversational noise: punctuation/case omission and mild fillers.
# Kept very sparse so the intent remains learnable.
noise_prefix = ["", "", "", "zara ", "bas ", "achha, ", "haan, "]
noise_suffix = ["", "", "", " na", " please", " ji"]
# "please" is used only sparsely as natural code-switch noise, not as dominant language.
punct = ["", "", "", "?", "!", "."]

def add_noise(s):
    if random.random() < 0.18:
        s = random.choice(noise_prefix) + s
    if random.random() < 0.12:
        s = s + random.choice(noise_suffix)
    if random.random() < 0.25:
        s = s.rstrip("!?.,") + random.choice(punct)
    if random.random() < 0.10:
        s = s.replace("  ", " ")
    return s

# Hand-crafted semantic sarcasm/noise for a minority, without changing the underlying intent.
sarcasm = {
"light_on":["haan, andhere mein hi baithe rahenge, {light} jala do","wah, kya roshni hai, {light} jala do"],
"light_off":["haan, roshni hi roshni chahiye kya, {light} bujha do","itni roshni kaafi hai, {light} band kar do"],
"fan_on":["wah, bina hawa ke maza aa raha hai, {fan} chala do","garmi mein bhi aaram hai, {fan} chala do"],
"fan_off":["haan, hawa hi hawa chalti rahe kya, {fan} band karo"],
"ac_on":["garmi mein jam jaayenge kya, {ac} chala do","wah, kya bhatti bani hai, {ac} on karo"],
"ac_off":["ab aur thand mein barf banna hai kya, {ac} band karo"],
"heater_on":["thand mein kaampte rahenge kya, {heater} chala do","wah, kamra itna thanda hai, {heater} on karo"],
"heater_off":["ab aur garam hona hai kya, {heater} band karo"],
"tv_on":["screen ko dekhte rahenge bina chalaye kya, {tv} on karo"],
"tv_off":["poori raat {tv} hi chalta rahe kya, band karo"],
"music_on":["itni khamoshi kyun hai, {music} chala do"],
"music_off":["padosiyon ko bhi sangeet sunana hai kya, {music} band karo"],
"door_open":["darwaze se baat karenge kya, {door} khol do"],
"door_close":["darwaza khula chhodna hi tha na, {door} band karo"],
"window_open":["hawa ko bahar hi rok ke rakhen kya, {window} khol do"],
"window_close":["thandi hawa ko ghar mein basana hai kya, {window} band karo"],
"lock_door":["ghar ko sabke liye khula chhod dein kya, {door} par {lock} laga do"],
"unlock_door":["tala laga hi rehne dein kya, {door} ka {lock} khol do"],
"alarm_on":["subah uthna hi nahi hai kya, {alarm} laga do"],
"alarm_off":["har waqt ghanti bajti rahe kya, {alarm} band karo"],
"temperature_up":["thand mein jamna hai kya, taapmaan badha do"],
"temperature_down":["garmi mein pakna hai kya, taapmaan ghata do"],
"temperature_status":["andaza lagayen ya {temperature} bata doge"],
"humidity_status":["hawa mein kitni nami hai, pata bhi hai kya, batao"],
"lights_status":["andhere mein dhoondhen kya, battiyon ka haal batao"],
"fans_status":["pankha chal raha hai ya hawa khud aa rahi hai, haal batao"],
"ac_status":["{ac} apne aap chal raha hai kya, sthiti batao"],
"heater_status":["{heater} chupchaap chal raha hai kya, haal batao"],
"tv_status":["{tv} band hai ya apni marzi se chal raha hai, batao"],
"music_status":["gaane baj rahe hain ya ghar bilkul chup hai, batao"],
"door_status":["darwaze khule chhodne ka iraada hai kya, sthiti batao"],
"window_status":["khidkiyan khuli chhodni hain kya, haal batao"],
"security_status":["ghar ki suraksha ka bharosa karein ya sthiti batao"],
"home_status":["ghar ka haal bhi pata hai ya nahi, batao"],
"good_morning":["suprabhat ji, din shuru kar dein ab"],
"good_night":["raat ho gayi hai, ab bhi jaagna hai kya, shubh raatri"],
"welcome_home":["ghar aa gaye, koi swagat karega ya khud hi kar lein"],
"leaving_home":["main nikal raha hoon, ghar ko sambhal lena"],
"sleep_mode":["ab sone dein ya ghar jagta rahe, sone ka mode laga do"],
"away_mode":["main bahar ja raha hoon, ghar ko waise hi chhod dein kya, bahar wala mode laga do"],
"movie_mode":["film dekhni hai, ab bhi batti jali rahegi kya, movie mode laga do"],
"party_mode":["thodi mehfil ho jaye, ghar ko udaas hi rakhen kya, jashn mode laga do"],
"emergency":["yeh mazaak nahi hai, aapatkaal hai, turant dhyan do"]
}

rows=[]
for cls in classes:
    candidates=set()
    # Build a large candidate pool from templates + lexical/context variation.
    templates = base[cls] + semantic.get(cls, []) + sarcasm.get(cls, [])
    attempts=0
    while len(candidates)<500 and attempts<5000:
        attempts += 1
        t=random.choice(templates)
        s=fill(t)
        # Add a few natural word-order/context variants.
        if random.random()<0.22 and cls in contexts:
            ctx=random.choice(contexts[cls])
            if "{light}" in t or "{fan}" in t or "{ac}" in t or "{heater}" in t:
                pass
            else:
                s = ctx + " " + s
        s=add_noise(s)
        # Avoid English-heavy variants: only allow a tiny amount of natural device terminology.
        # Ensure no accidental duplicate.
        if s and s.lower() not in candidates:
            candidates.add(s.lower())
    # If some classes have fewer natural combinations, expand by controlled prefixes/suffixes.
    fallback=list(candidates)
    i=0
    while len(candidates)<500:
        s=fallback[i % len(fallback)]
        variant = random.choice(["abhi ","zara ","bas ","haan, ","achha, ",""]) + s
        if random.random()<0.35:
            variant += random.choice([" na"," ji"," ab"," bas"])
        candidates.add(variant.strip())
        i+=1
    for s in list(candidates)[:500]:
        rows.append((s,cls))

random.shuffle(rows)

out="./data/raw/home_intelligence_21500_roman_hindi_semantic_noise.csv"
with open(out,"w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f)
    w.writerow(["Input","Label"])
    w.writerows(rows)

# Validate exact balance, columns, and no accidental blank rows.
from collections import Counter
counts=Counter(r[1] for r in rows)
assert len(rows)==43*500
assert set(counts)==set(classes)
assert all(v==500 for v in counts.values())
assert all(r[0].strip() and r[1].strip() for r in rows)

print(f"Created: {out}")
print(f"Rows: {len(rows)} | Classes: {len(classes)} | Rows/class: 500")
