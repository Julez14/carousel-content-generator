"""Configuration settings for the TikTok carousel bot."""

from __future__ import annotations

# Account configurations with posting schedules and TikTok usernames
ACCOUNTS = [
    {
        "name": "@skincaretips",
        "tiktok_username": "XYZ",
        "post_times": ["07:00", "11:00", "15:00", "19:00"],
        "webhook_url": "https://discord.com/api/webhooks/..."
    },
]

# Google Drive folder mappings
DRIVE_FOLDERS = {
    "HOOK": "hook-photos",
    "SCREEN": "product-screenshots", 
    "CTA": "cta-photos"
}

# Call-to-action text options
CTA_TEXTS = [
    "Follow for more skincare tips! 💫",
    "Save this post for later! ✨", 
    "Tag someone who needs to see this! 👇",
    "What's your biggest skincare concern? 💭",
    "Follow for daily skincare content! 🌟",
    "Follow for more product reccomendations! ✨",
    "Follow for more product scans! ✨"
]

# Hashtag generation settings
HASHTAG_COUNT = 12

# Predefined list of skincare hashtags
ALL_HASHTAGS = [
    "#koreanskincare", "#kskincare", "#skincare", "#skintypes",
    "#skincareroutine", "#korea", "#korean", "#dry", "#combo", 
    "#combination", "#oily", "#2025", "#kbeauty", "#fy", "#fyp", "#fyp",
    "#foryou", "#foryoupage", "#viral", "#acne", "#fungalacne", 
    "#viralskincare", "#skincareroutinetips", "#glassskin", "#hormonalacne",
    "#beauty", "#sensitiveskin", "#skincaretips", "#skincarereview", 
    "#koreanskincareproducts", "#acnetips", "#acnescars"
]

# Pre-generated hooks to avoid API calls
PREGENERATED_HOOKS = [
    "Products that completely changed my skin texture 😭",
    "Products I'd buy again with my last dollar 💸",
    "Skincare that made me *finally* stop picking 😳",
    "Products that fixed what dermatologists couldn't 😤",
    "Skincare that made me love my bare face 😊",
    "Products that ended my 6-year acne battle 🛑",
    "Skincare that actually made me glow IRL ✨",
    "Products that gave me glass skin overnight 🪞",
    "Skincare that made me ditch foundation 😮‍💨",
    "Products I regret not trying sooner 😩",
    "Skincare that turned my routine into results 🔁",
    "Products that saved my skin barrier 🧪",
    "Skincare I use every single day 🗓️",
    "Products that healed my skin from within 🌿",
    "Skincare that *actually* works on oily skin 🫧",
    "Products that made me feel pretty again 💖",
    "Skincare that gave me confidence without makeup 💁",
    "Products that cleared my hormonal breakouts 😭",
    "Skincare I'd gatekeep if I was selfish 🔒",
    "Products that made me fall in love w/ skincare 💘",
    "Skincare that works even when I'm lazy 🛋️",
    "Products that gave me compliments all week 😳",
    "Skincare that made me believe in miracles 🪄",
    "Products that fixed my uneven skin tone 🎯",
    "Skincare I wish I had in high school 📚",
    "Products I'll be using when I'm 80 👵",
    "Skincare that survived my breakup with makeup 💔",
    "Products I thought were overhyped… until I tried them 😶",
    "Skincare that worked better than prescriptions 💊",
    "Products that erased years of bad habits 🧼",
    "Skincare that made me glow like a K-drama lead 🎬",
    "Products that worked faster than I expected ⏱️",
    "Skincare I trust with my worst skin days 🌧️",
    "Products I *always* bring on vacation 🧳",
    "Skincare that worked after everything else failed 😵‍💫",
    "Products that saved me from another breakout 😤",
    "Skincare that works while I sleep 💤",
    "Products that fixed my skin in 2 weeks 🗓️",
    "Skincare that made my ex text me back 📱",
    "Products that made me stop using filters 📵",
    "Skincare that feels expensive but isn't 💅",
    "Products that gave me baby-smooth skin 🍼",
    "Skincare that faded my dark spots fast ⚡",
    "Products I use when I want compliments 🗣️",
    "Skincare that *actually* controls my oil 🧴",
    "Products I discovered by accident and now swear by 🤯",
    "Skincare that made my skin feel brand new 🧖",
    "Products that turned my skin around completely 🔄",
    "Skincare that works even in Canadian winters ❄️",
    "Products that give me *that* glow on camera 🎥",
    "Skincare that's worth every single penny 💵",
    "Products I use when my skin's freaking out 😫",
    "Skincare that made me fall in love with SPF 🌞",
    "Products that work on textured acne-prone skin 🫠",
    "Skincare that *finally* fixed my pores 🕳️",
    "Products that made me stop touching my face 🙅",
    "Skincare that made me feel 'clean girl' ready 🩷",
    "Products I keep rebuying no matter what 🔁",
    "Skincare that makes me feel like a model 📸",
    "Products that helped my skin *and* self-esteem ❤️",
    "Skincare that works even on bad diet days 🍟",
    "Products I trust with my life (and skin) 🛟",
    "Skincare I'd give my past self ASAP ⏳",
    "Products I use before every big event 📆",
    "Skincare that made me cancel my facial 😌",
    "Products that made my skin look expensive 💎",
    "Skincare that made me believe in routines 📋",
    "Products that actually helped my skin recover 🧃",
    "Skincare that's always in my top drawer 📥",
    "Products I stole from my sister and kept 😅",
    "Skincare that makes me *feel* rich 👛",
    "Products I discovered on TikTok that *work* 🔍",
    "Skincare that's way better than it looks 🧼",
    "Products that shocked me with how good they are 😳",
    "Skincare that got me compliments from strangers 🗯️",
    "Products that helped me feel cute again 🫶",
    "Skincare that helped my skin feel calm 🌱",
    "Products that gave me real results, not hope 🫥",
    "Skincare that helps me fake 8 hours of sleep 🌙",
    "Products I tell all my friends about 📣",
    "Skincare that actually helped with redness 🍅",
    "Products that made me stop experimenting 😮‍💨",
    "Skincare that worked for me and my mom 👩‍👧",
    "Products that deserve all the hype 🥵",
    "Skincare I'd save in a house fire 🔥",
    "Products that never let me down 💯",
    "Skincare that works even when I don't 🐌",
    "Products that fixed my texture in days 😲",
    "Skincare that made me feel ✨ put together ✨",
    "Products I use when I want flawless skin 🪞",
    "Skincare that I'll never stop buying 💳",
    "Products that made my skin look filtered 🧃",
    "Skincare that gives me compliments weekly 🫢",
    "Products that made my skin look alive again 🧬",
    "Skincare that gave me confidence again 🧘",
    "Products that work with zero irritation 🧴",
    "Skincare that actually made my pores smaller 🔬",
    "Products that *finally* gave me real glow ✨",
    "Skincare that made my skin feel hydrated all day 💧",
    "Products I won't travel without ever again 🌍",
    "Skincare that was worth the entire haul 🛍️",
    "Products I keep rebuying even broke 😅",
    "Skincare that gave me model-off-duty skin 🕶️",
    "Products that work better than they should 🧠",
    "Skincare that works no matter the season 🌦️",
    "Products that worked better than facials 🧖‍♀️",
    "Skincare that goes viral for a reason 📈",
    "Products I use when my skin is angry 😠",
    "Skincare that actually gave me bounce 🏀",
    "Products I trust for first dates and interviews 🫣"
]

# Timezone for scheduling
TIMEZONE = "America/Toronto"

# Text overlay settings
TEXT_SETTINGS = {
    "font_size": 56,                # Larger for better impact
    "font_color": (255, 255, 255),  # White
    "stroke_color": (0, 0, 0),      # Black
    "stroke_width": 2,              # Thicker stroke for better readability
    "y_position_percent": 70,       # 70% down from top
    "max_width_percent": 85,        # Slightly narrower for better text wrapping
}

# Hook slide specific text settings
HOOK_TEXT_SETTINGS = {
    "font_size": 48,                # Standard size for hook
    "font_color": (255, 255, 255),  # White
    "stroke_color": (0, 0, 0),      # Black
    "stroke_width": 2,              # Thicker stroke for better readability
    "y_position_percent": 70,       # Lower positioning for hook
    "max_width_percent": 85,        # Slightly narrower for better text wrapping
}

# CTA slide specific text settings
CTA_TEXT_SETTINGS = {
    "font_size": 64,                # Reduced from 88 to prevent text cutoff
    "font_color": (255, 255, 255),  # White
    "stroke_color": (0, 0, 0),      # Black
    "stroke_width": 2,              # Thicker stroke for better readability
    "y_position_percent": 50,       # Centered vertically for CTA
    "max_width_percent": 85,        # Slightly narrower for better text wrapping
}

# Image quality settings
IMAGE_QUALITY = 90

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds 