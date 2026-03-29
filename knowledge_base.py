"""
Voltex Repair Triage Agent
knowledge_base.py — Synthetic Parts Catalogue and Repair Database

Contains:
  - Product categories and common fault types
  - Parts catalogue with availability and cost
  - Repair complexity matrix
  - Technician skill requirements
  - BER (Beyond Economical Repair) thresholds
"""

# ─────────────────────────────────────────────
# FAULT TAXONOMY
# ─────────────────────────────────────────────

FAULT_CATEGORIES = {
    "laptop": {
        "display": [
    "cracked screen", "crack", "cracked", "broken screen",
    "screen lines", "backlight failure", "flickering display",
    "no display", "dead pixels", "smashed screen", "shattered screen",
    "screen damage", "display damage",
        ],
        "battery": [
            "battery not charging", "battery drains fast",
            "swollen battery", "won't power on",
        ],
        "keyboard": [
            "keys not working", "liquid damage keyboard",
            "trackpad not responding", "keyboard backlight failure",
        ],
        "motherboard": [
            "won't turn on", "random shutdowns", "overheating",
            "USB ports not working", "wifi not working",
        ],
        "storage": [
            "slow performance", "not booting", "clicking noise",
            "files corrupted", "SSD failure",
        ],
        "cooling": [
            "fan noise", "overheating", "thermal throttling",
            "fan not spinning",
        ],
    },
    "phone": {
        "screen": [
            "cracked screen", "touch not working", "screen lines",
            "no display", "screen burn-in",
        ],
        "battery": [
            "battery drains fast", "won't charge", "swollen battery",
            "random shutdowns",
        ],
        "camera": [
            "camera not working", "blurry photos", "front camera failure",
            "camera app crashes",
        ],
        "connectivity": [
            "no signal", "wifi not connecting", "bluetooth not working",
            "charging port damage",
        ],
        "liquid": [
            "liquid damage", "speaker muffled", "microphone not working",
            "buttons not responding",
        ],
    },
    "tv": {
        "display": [
            "no picture", "screen lines", "backlight failure",
            "dead pixels", "HDMI not working", "image retention",
        ],
        "audio": [
            "no sound", "distorted audio", "speaker failure",
            "volume control not working",
        ],
        "smart": [
            "smart features not working", "apps crashing",
            "wifi not connecting", "remote not pairing",
        ],
        "power": [
            "won't turn on", "turns off randomly", "standby light flashing",
        ],
    },
    "washing_machine": {
        "drum": [
            "drum not spinning", "loud banging noise", "drum bearing failure",
            "drum loose",
        ],
        "water": [
            "not filling with water", "not draining", "leaking water",
            "water on floor",
        ],
        "electrical": [
            "won't start", "programme not completing", "error code displayed",
            "door won't open", "door won't lock",
        ],
        "motor": [
            "motor failure", "burning smell", "won't spin",
            "noisy spin cycle",
        ],
    },
    "fridge_freezer": {
        "cooling": [
            "not cooling", "not freezing", "temperature too warm",
            "frost build-up", "compressor noise",
        ],
        "electrical": [
            "display not working", "lights not working",
            "ice maker failure", "water dispenser failure",
        ],
        "mechanical": [
            "door seal damaged", "drawer broken", "shelves broken",
            "door not closing properly",
        ],
    },
    "dishwasher": {
        "washing": [
            "dishes not clean", "not washing properly",
            "spray arms blocked", "detergent not dissolving",
        ],
        "water": [
            "not filling", "not draining", "leaking",
            "standing water at bottom",
        ],
        "electrical": [
            "won't start", "programme not completing",
            "error code", "door latch broken",
        ],
    },
}


# ─────────────────────────────────────────────
# PARTS CATALOGUE
# ─────────────────────────────────────────────

PARTS_CATALOGUE = {
    # Laptop parts
    "LP-SCR-001": {
        "name"        : "Laptop LCD screen assembly (15.6 inch FHD)",
        "category"    : "laptop",
        "component"   : "display",
        "cost"        : 89.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["computing"],
    },
    "LP-SCR-002": {
        "name"        : "Laptop OLED screen assembly (14 inch)",
        "category"    : "laptop",
        "component"   : "display",
        "cost"        : 189.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["computing"],
    },
    "LP-BAT-001": {
        "name"        : "Laptop battery (generic, 4-cell 60Wh)",
        "category"    : "laptop",
        "component"   : "battery",
        "cost"        : 34.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["computing"],
    },
    "LP-BAT-002": {
        "name"        : "Laptop battery (Apple MacBook compatible)",
        "category"    : "laptop",
        "component"   : "battery",
        "cost"        : 89.99,
        "availability": "low_stock",
        "lead_days"   : 2,
        "fits"        : ["computing"],
    },
    "LP-KEY-001": {
        "name"        : "Laptop keyboard assembly (UK layout)",
        "category"    : "laptop",
        "component"   : "keyboard",
        "cost"        : 44.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["computing"],
    },
    "LP-FAN-001": {
        "name"        : "Laptop cooling fan assembly",
        "category"    : "laptop",
        "component"   : "cooling",
        "cost"        : 24.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["computing"],
    },
    "LP-SSD-001": {
        "name"        : "SSD M.2 NVMe 512GB replacement",
        "category"    : "laptop",
        "component"   : "storage",
        "cost"        : 54.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["computing"],
    },
    "LP-MTH-001": {
        "name"        : "Laptop motherboard (generic)",
        "category"    : "laptop",
        "component"   : "motherboard",
        "cost"        : 249.99,
        "availability": "low_stock",
        "lead_days"   : 5,
        "fits"        : ["computing"],
    },

    # Phone parts
    "PH-SCR-001": {
        "name"        : "Phone screen assembly (Android generic)",
        "category"    : "phone",
        "component"   : "screen",
        "cost"        : 49.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["phones"],
    },
    "PH-SCR-002": {
        "name"        : "Phone screen assembly (Samsung AMOLED)",
        "category"    : "phone",
        "component"   : "screen",
        "cost"        : 89.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["phones"],
    },
    "PH-SCR-003": {
        "name"        : "Phone screen assembly (Apple authorised)",
        "category"    : "phone",
        "component"   : "screen",
        "cost"        : 129.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["phones"],
    },
    "PH-BAT-001": {
        "name"        : "Phone battery replacement (Android generic)",
        "category"    : "phone",
        "component"   : "battery",
        "cost"        : 19.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["phones"],
    },
    "PH-CHG-001": {
        "name"        : "Phone charging port assembly",
        "category"    : "phone",
        "component"   : "connectivity",
        "cost"        : 29.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["phones"],
    },

    # TV parts
    "TV-PNL-001": {
        "name"        : "TV LCD panel (43 inch FHD)",
        "category"    : "tv",
        "component"   : "display",
        "cost"        : 189.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["tv_audio"],
    },
    "TV-PNL-002": {
        "name"        : "TV LCD panel (55 inch 4K)",
        "category"    : "tv",
        "component"   : "display",
        "cost"        : 289.99,
        "availability": "low_stock",
        "lead_days"   : 3,
        "fits"        : ["tv_audio"],
    },
    "TV-PNL-003": {
        "name"        : "TV OLED panel (55 inch)",
        "category"    : "tv",
        "component"   : "display",
        "cost"        : 489.99,
        "availability": "out_of_stock",
        "lead_days"   : 14,
        "fits"        : ["tv_audio"],
    },
    "TV-BLT-001": {
        "name"        : "TV backlight strip replacement",
        "category"    : "tv",
        "component"   : "display",
        "cost"        : 39.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["tv_audio"],
    },
    "TV-PWR-001": {
        "name"        : "TV power supply board",
        "category"    : "tv",
        "component"   : "power",
        "cost"        : 49.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["tv_audio"],
    },
    "TV-SPK-001": {
        "name"        : "TV speaker assembly replacement",
        "category"    : "tv",
        "component"   : "audio",
        "cost"        : 34.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["tv_audio"],
    },

    # Washing machine parts
    "WM-BRG-001": {
        "name"        : "Washing machine drum bearing kit",
        "category"    : "washing_machine",
        "component"   : "drum",
        "cost"        : 44.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["white_goods"],
    },
    "WM-PMP-001": {
        "name"        : "Washing machine drain pump",
        "category"    : "washing_machine",
        "component"   : "water",
        "cost"        : 29.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["white_goods"],
    },
    "WM-DOR-001": {
        "name"        : "Washing machine door seal (universal)",
        "category"    : "washing_machine",
        "component"   : "water",
        "cost"        : 19.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["white_goods"],
    },
    "WM-MOT-001": {
        "name"        : "Washing machine motor (brush type)",
        "category"    : "washing_machine",
        "component"   : "motor",
        "cost"        : 89.99,
        "availability": "low_stock",
        "lead_days"   : 3,
        "fits"        : ["white_goods"],
    },
    "WM-MOT-002": {
        "name"        : "Washing machine inverter motor",
        "category"    : "washing_machine",
        "component"   : "motor",
        "cost"        : 149.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["white_goods"],
    },
    "WM-PCB-001": {
        "name"        : "Washing machine control board (PCB)",
        "category"    : "washing_machine",
        "component"   : "electrical",
        "cost"        : 119.99,
        "availability": "low_stock",
        "lead_days"   : 5,
        "fits"        : ["white_goods"],
    },

    # Fridge-freezer parts
    "FF-CMP-001": {
        "name"        : "Fridge compressor (universal R600a)",
        "category"    : "fridge_freezer",
        "component"   : "cooling",
        "cost"        : 199.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["white_goods"],
    },
    "FF-FAN-001": {
        "name"        : "Fridge evaporator fan motor",
        "category"    : "fridge_freezer",
        "component"   : "cooling",
        "cost"        : 24.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["white_goods"],
    },
    "FF-SLR-001": {
        "name"        : "Fridge door seal replacement",
        "category"    : "fridge_freezer",
        "component"   : "mechanical",
        "cost"        : 14.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["white_goods"],
    },
    "FF-THM-001": {
        "name"        : "Fridge thermostat / temperature sensor",
        "category"    : "fridge_freezer",
        "component"   : "cooling",
        "cost"        : 19.99,
        "availability": "in_stock",
        "lead_days"   : 0,
        "fits"        : ["white_goods"],
    },
}


# ─────────────────────────────────────────────
# REPAIR COMPLEXITY MATRIX
# ─────────────────────────────────────────────

REPAIR_COMPLEXITY = {
    "laptop": {
        "display"    : {"complexity": "medium", "labour_hours": 1.5, "skill": "tech_bar"},
        "battery"    : {"complexity": "easy",   "labour_hours": 0.5, "skill": "tech_bar"},
        "keyboard"   : {"complexity": "easy",   "labour_hours": 1.0, "skill": "tech_bar"},
        "cooling"    : {"complexity": "easy",   "labour_hours": 1.0, "skill": "tech_bar"},
        "storage"    : {"complexity": "easy",   "labour_hours": 1.0, "skill": "tech_bar"},
        "motherboard": {"complexity": "hard",   "labour_hours": 3.0, "skill": "newark"},
    },
    "phone": {
        "screen"     : {"complexity": "easy",   "labour_hours": 0.75, "skill": "tech_bar"},
        "battery"    : {"complexity": "easy",   "labour_hours": 0.5,  "skill": "tech_bar"},
        "camera"     : {"complexity": "medium", "labour_hours": 1.0,  "skill": "newark"},
        "connectivity": {"complexity": "medium", "labour_hours": 1.5, "skill": "newark"},
        "liquid"     : {"complexity": "hard",   "labour_hours": 2.0,  "skill": "newark"},
    },
    "tv": {
        "display"    : {"complexity": "hard",   "labour_hours": 2.0, "skill": "newark"},
        "audio"      : {"complexity": "medium", "labour_hours": 1.5, "skill": "newark"},
        "smart"      : {"complexity": "easy",   "labour_hours": 0.5, "skill": "tech_bar"},
        "power"      : {"complexity": "medium", "labour_hours": 1.5, "skill": "newark"},
    },
    "washing_machine": {
        "drum"       : {"complexity": "hard",   "labour_hours": 3.0, "skill": "engineer"},
        "water"      : {"complexity": "medium", "labour_hours": 1.5, "skill": "engineer"},
        "electrical" : {"complexity": "medium", "labour_hours": 2.0, "skill": "engineer"},
        "motor"      : {"complexity": "hard",   "labour_hours": 3.0, "skill": "engineer"},
    },
    "fridge_freezer": {
        "cooling"    : {"complexity": "hard",   "labour_hours": 2.5, "skill": "engineer"},
        "electrical" : {"complexity": "medium", "labour_hours": 1.5, "skill": "engineer"},
        "mechanical" : {"complexity": "easy",   "labour_hours": 0.5, "skill": "engineer"},
    },
    "dishwasher": {
        "washing"    : {"complexity": "medium", "labour_hours": 1.5, "skill": "engineer"},
        "water"      : {"complexity": "medium", "labour_hours": 1.5, "skill": "engineer"},
        "electrical" : {"complexity": "medium", "labour_hours": 2.0, "skill": "engineer"},
    },
}

# Labour cost per hour by skill level
LABOUR_RATES = {
    "tech_bar" : 35.0,   # In-store Tech Bar technician
    "newark"   : 45.0,   # Newark Repair Centre specialist
    "engineer" : 55.0,   # Field engineer (white goods)
}

# BER threshold — if repair cost > X% of replacement value, recommend replace
BER_THRESHOLD = 0.65

# Repair paths
REPAIR_PATHS = {
    "tech_bar" : "In-store Tech Bar repair (same day, 60-90 minutes)",
    "newark"   : "Newark Repair Centre (5 working days, collection required)",
    "engineer" : "Home engineer visit (3-7 working days)",
    "replace"  : "Beyond economical repair — recommend replacement",
}

# Technician skill descriptions
SKILL_DESCRIPTIONS = {
    "tech_bar" : "Tech Bar certified technician — screen replacements, batteries, keyboards",
    "newark"   : "Newark specialist — complex electronics, liquid damage, motherboard work",
    "engineer" : "Field engineer — white goods, appliance installation and repair",
}