"""data/characters.py"""
HEROES = {
    "aldric": {
        "name": "Aldric", "title": "Şövalye", "color": (80, 120, 200),
        "description": "Onurlu, karizmatik. Kılıcına güvenir, büyüden anlamaz.",
        "stats": {"str": 8, "spd": 5, "int": 2, "charm": 7, "luck": 4},
        "good_at": ["combat", "negotiation"], "bad_at": ["stealth", "magic"],
    },
    "seraphel": {
        "name": "Seraphel", "title": "Büyücü", "color": (140, 60, 180),
        "description": "Soğuk, hesapçı. Sırrı çok, sözü az.",
        "stats": {"str": 2, "spd": 4, "int": 9, "charm": 3, "luck": 5},
        "good_at": ["magic", "research"], "bad_at": ["combat", "negotiation"],
    },
    "elysia": {
        "name": "Elysia", "title": "Okçu", "color": (60, 160, 90),
        "description": "Genç, neşeli ama savaşçı ruhu var. Yaralı ama dimdik.",
        "stats": {"str": 4, "spd": 9, "int": 5, "charm": 6, "luck": 8},
        "good_at": ["stealth", "negotiation"], "bad_at": ["magic", "combat"],
    },
}

# NOT: Oyundaki affection değerleri 0-100 skalasında saklanıyor.
AFFECTION_BANDS = [
    (  0, 20, "Düşman",   (160,  40,  40), -0.20),
    ( 21, 40, "Mesafeli", (190, 110,  30), -0.10),
    ( 41, 60, "Nötr",     (150, 140,  60),  0.00),
    ( 61, 80, "Dost",     ( 50, 155,  70), +0.10),
    ( 81,100, "Sadık",    (200, 160,  40), +0.20),
]

def get_affection_info(score):
    for lo, hi, lbl, col, delta in AFFECTION_BANDS:
        if lo <= score <= hi:
            return lbl, col, delta
    return "Nötr", (150, 140, 60), 0.0

def build_runtime_heroes():
    result = {}
    for key, h in HEROES.items():
        result[key] = {
            **h, "stats": dict(h["stats"]),
            "alive": True, "on_mission": False,
            "tired": 0,        # Integer (0-100), Boolean değil!
            "morale": 50,      # Başlangıç morali (0-100)
            "affection": 50,   # 0-100 skalasında başlangıç
            "morale_bonus": 0.0,
            "chat_completed": False,
        }
    return result

def calculate_success_chance(hero_key, mission_type, hero_rt):
    base_def = HEROES.get(hero_key, {})
    stats    = hero_rt.get("stats", {})
    base     = 0.40
    bonus_map = {
        "combat": ("str", 0.055), "stealth": ("spd", 0.055),
        "magic":  ("int", 0.055), "negotiation": ("charm", 0.055),
    }
    if mission_type in bonus_map:
        sk, m = bonus_map[mission_type]
        base += stats.get(sk, 0) * m
    base += stats.get("luck", 0) * 0.012
    if mission_type in base_def.get("good_at", []):  base += 0.15
    if mission_type in base_def.get("bad_at",  []):  base -= 0.10
    if hero_rt.get("tired"):       base -= 0.10
    base += hero_rt.get("morale_bonus", 0.0)
    _, _, aff_delta = get_affection_info(hero_rt.get("affection", 5))
    base += aff_delta
    return max(0.05, min(0.95, base))