# Dummy story.py module for testing
import random

DAILY_HEROES = [
    {
        "hero": "Aldric",
        "intro_lines": [
            "Selam Simyacı, ben Aldric.",
            "Bugün orman devriyesine liderlik edeceğim.",
            "Güvenliğimiz için bana bir Sağlık İksiri hazırlamalısın."
        ],
        "request": "Sağlık İksiri",
        "reward": 80
    },
    {
        "hero": "Seraphel",
        "intro_lines": [
            "Merhaba Simyacı.",
            "Kriptalardaki gölgeler oldukça hareketli görünüyor.",
            "Hızlı hareket edebilmek için bir Hız İksiri istiyorum."
        ],
        "request": "Hız İksiri",
        "reward": 80
    },
    {
        "hero": "Elysia",
        "intro_lines": [
            "Selam Simyacı, ben Elysia.",
            "Yarın son büyük savaşa çıkıyoruz.",
            "Kalkanlarını aşabilmek için bir Güç İksiri hazırlamalısın."
        ],
        "request": "Güç İksiri",
        "reward": 80
    }
]

TOWNSFOLK_POOL = [
    {
        "name": "Demirci Garrick",
        "dialogue_lines": [
            "Kolay gelsin Simyacı.",
            "Bugün örsleri kaldırmak için ekstra güce ihtiyacım var.",
            "Bana bir Güç İksiri verir misin?"
        ],
        "request": "Güç İksiri",
        "reward": 40
    },
    {
        "name": "Gözcü Evelyn",
        "dialogue_lines": [
            "İyi günler.",
            "Kuzey tepelerini haritalandırıyorum.",
            "Yolu hızlıca aşmak için Hız İksiri alabilir miyim?"
        ],
        "request": "Hız İksiri",
        "reward": 40
    },
    {
        "name": "Aktar Fiona",
        "dialogue_lines": [
            "Merhaba simya ustası.",
            "Malzeme toplarken yoruluyorum.",
            "Bana bir Sağlık İksiri yapar mısın?"
        ],
        "request": "Sağlık İksiri",
        "reward": 40
    }
]

def get_two_townsfolk():
    """Returns two random townsfolk from the pool."""
    return random.sample(TOWNSFOLK_POOL, 2)

NIGHT_CHATS = {
    "Aldric": {
        1: {
            "text": "I feel the pressure of leadership, Alchemist. Am I doing enough for the squad?",
            "choices": {
                "A": {"text": "Encourage him: 'You are doing great, Aldric.' (+5 Aff, +10 Mor, -5 Tired)", "affection_delta": 5, "morale_bonus": 10, "tired_relief": 5},
                "B": {"text": "Listen silently: 'I hear you.' (+10 Aff, +0 Mor, -10 Tired)", "affection_delta": 10, "morale_bonus": 0, "tired_relief": 10},
                "C": {"text": "Challenge him: 'Leadership requires sacrifices.' (-5 Aff, +20 Mor, +0 Tired)", "affection_delta": -5, "morale_bonus": 20, "tired_relief": 0}
            }
        },
        2: {
            "text": "The battles are getting tougher. The men look to me for strength, but I feel weak.",
            "choices": {
                "A": {"text": "Comfort him. (+5 Aff, +10 Mor, -5 Tired)", "affection_delta": 5, "morale_bonus": 10, "tired_relief": 5},
                "B": {"text": "Offer rest. (+10 Aff, +0 Mor, -15 Tired)", "affection_delta": 10, "morale_bonus": 0, "tired_relief": 15},
                "C": {"text": "Push him hard. (-10 Aff, +25 Mor, +5 Tired)", "affection_delta": -10, "morale_bonus": 25, "tired_relief": -5}
            }
        },
        3: {
            "text": "This is our final stand. Whatever happens tomorrow, it was an honor working with you.",
            "choices": {
                "A": {"text": "Salute him. (+10 Aff, +10 Mor, -5 Tired)", "affection_delta": 10, "morale_bonus": 10, "tired_relief": 5},
                "B": {"text": "Drink together. (+15 Aff, +5 Mor, -10 Tired)", "affection_delta": 15, "morale_bonus": 5, "tired_relief": 10},
                "C": {"text": "Focus on victory. (+0 Aff, +25 Mor, +0 Tired)", "affection_delta": 0, "morale_bonus": 25, "tired_relief": 0}
            }
        }
    },
    "Seraphel": {
        1: {
            "text": "My spells require complete focus, but my mind wanders. How do you find peace?",
            "choices": {
                "A": {"text": "Suggest meditation. (+5 Aff, +10 Mor, -5 Tired)", "affection_delta": 5, "morale_bonus": 10, "tired_relief": 5},
                "B": {"text": "Share a brew. (+10 Aff, +5 Mor, -10 Tired)", "affection_delta": 10, "morale_bonus": 5, "tired_relief": 10},
                "C": {"text": "Tell her to focus. (-5 Aff, +15 Mor, +0 Tired)", "affection_delta": -5, "morale_bonus": 15, "tired_relief": 0}
            }
        },
        2: {
            "text": "The shadows whisper of danger. Do you believe we can survive this?",
            "choices": {
                "A": {"text": "Reassure her. (+5 Aff, +10 Mor, -5 Tired)", "affection_delta": 5, "morale_bonus": 10, "tired_relief": 5},
                "B": {"text": "Stand strong. (+10 Aff, +5 Mor, -10 Tired)", "affection_delta": 10, "morale_bonus": 5, "tired_relief": 10},
                "C": {"text": "Doubt. (-10 Aff, +0 Mor, +10 Tired)", "affection_delta": -10, "morale_bonus": 0, "tired_relief": -10}
            }
        },
        3: {
            "text": "The magic in this world is fading, but our connection remains strong.",
            "choices": {
                "A": {"text": "Accept. (+10 Aff, +10 Mor, -5 Tired)", "affection_delta": 10, "morale_bonus": 10, "tired_relief": 5},
                "B": {"text": "Smile. (+15 Aff, +0 Mor, -10 Tired)", "affection_delta": 15, "morale_bonus": 0, "tired_relief": 10},
                "C": {"text": "Ignore. (-5 Aff, +15 Mor, +0 Tired)", "affection_delta": -5, "morale_bonus": 15, "tired_relief": 0}
            }
        }
    },
    "Elysia": {
        1: {
            "text": "I miss the forests of my home. The city smells of smoke and metal.",
            "choices": {
                "A": {"text": "Reminisce: 'I miss the green too.' (+10 Aff, +5 Mor, -5 Tired)", "affection_delta": 10, "morale_bonus": 5, "tired_relief": 5},
                "B": {"text": "Listen: 'Tell me about it.' (+15 Aff, +0 Mor, -10 Tired)", "affection_delta": 15, "morale_bonus": 0, "tired_relief": 10},
                "C": {"text": "Practical: 'We must adapt.' (-5 Aff, +15 Mor, +5 Tired)", "affection_delta": -5, "morale_bonus": 15, "tired_relief": -5}
            }
        },
        2: {
            "text": "My bow feels heavier today. My shoulders ache from tension.",
            "choices": {
                "A": {"text": "Massage them. (+10 Aff, +5 Mor, -15 Tired)", "affection_delta": 10, "morale_bonus": 5, "tired_relief": 15},
                "B": {"text": "Rest. (+12 Aff, +0 Mor, -12 Tired)", "affection_delta": 12, "morale_bonus": 0, "tired_relief": 12},
                "C": {"text": "Train. (-5 Aff, +20 Mor, +5 Tired)", "affection_delta": -5, "morale_bonus": 20, "tired_relief": -5}
            }
        },
        3: {
            "text": "After this is over, will you visit the ancient woods with me?",
            "choices": {
                "A": {"text": "Promise. (+15 Aff, +10 Mor, -5 Tired)", "affection_delta": 15, "morale_bonus": 10, "tired_relief": 5},
                "B": {"text": "Laugh. (+10 Aff, +5 Mor, -10 Tired)", "affection_delta": 10, "morale_bonus": 5, "tired_relief": 10},
                "C": {"text": "Refuse. (-15 Aff, +20 Mor, +0 Tired)", "affection_delta": -15, "morale_bonus": 20, "tired_relief": 0}
            }
        }
    }
}