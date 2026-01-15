# keyword_weights.py

# -----------------------------------------------------------------------------
# 1. SCORING SCALES (ระบบคะแนนแบบเส้นตรง)
# -----------------------------------------------------------------------------
AGREEMENT_KEYWORDS = {
    "strongly agree": 5, "เห็นด้วยอย่างยิ่ง": 5, "มากที่สุด": 5, "จริงที่สุด": 5,
    "agree": 4, "เห็นด้วย": 4, "ค่อนข้างจริง": 4, "มาก": 4,
    "neutral": 3, "เฉยๆ": 3, "ปานกลาง": 3, "ไม่แน่ใจ": 3,
    "disagree": 2, "ไม่เห็นด้วย": 2, "น้อย": 2, "ไม่ค่อยจริง": 2,
    "strongly disagree": 1, "ไม่เห็นด้วยอย่างยิ่ง": 1, "น้อยที่สุด": 1, "ไม่จริงเลย": 1
}

FREQUENCY_KEYWORDS = {
    "always": 5, "สม่ำเสมอ": 5, "ประจำ": 5, "ทุกวัน": 5, "บ่อยมาก": 5,
    "often": 4, "บ่อย": 4, "ค่อนข้างบ่อย": 4,
    "sometimes": 3, "บางครั้ง": 3, "นานๆ ครั้ง": 3,
    "rarely": 2, "แทบจะไม่": 2, "น้อยครั้ง": 2,
    "never": 1, "ไม่เคย": 1
}

# -----------------------------------------------------------------------------
# 2. CONTEXT MAPPING (จับคู่ Keyword -> หมวดหมู่ความสนใจ/บริบท)
# -----------------------------------------------------------------------------
CONTEXT_KEYWORDS = {
    # Work & Career
    "leadership": ["นำทีม", "หัวหน้า", "ตัดสินใจ", "บริหาร", "lead", "manage"],
    "teamwork": ["ทำงานร่วมกัน", "ทีม", "ช่วยเหลือ", "team", "collaborate"],
    "sustainability": ["สิ่งแวดล้อม", "ยั่งยืน", "ธรรมชาติ", "green", "environment"],
    "technology": ["เทคโนโลยี", "tech", "ai", "app", "digital", "gadget", "ออนไลน์"],
    "finance": ["การเงิน", "ลงทุน", "ออม", "ราคา", "คุ้มค่า", "finance", "budget", "price"],

    # Lifestyle
    "social": ["เพื่อน", "สังสรรค์", "สังคม", "party", "social", "meet"],
    "health": ["สุขภาพ", "ออกกำลังกาย", "อาหาร", "health", "fitness", "gym"],
    "leisure": ["พักผ่อน", "เที่ยว", "ดูหนัง", "relax", "travel", "game"],
    "learning": ["เรียนรู้", "ศึกษา", "พัฒนา", "learn", "study", "research"],
}

# -----------------------------------------------------------------------------
# 3. TRAIT MAPPING (จับคู่ตัวเลือก -> นิสัย/บุคลิก)
# -----------------------------------------------------------------------------
# Format: "Keyword found in option": ["Associated Trait 1", "Associated Trait 2"]
OPTION_TO_TRAIT = {
    # Speed & Risk
    "เร็ว": ["Impulsive", "Risk-taker"],
    "ด่วน": ["Impulsive", "Risk-taker"],
    "ทันที": ["Impulsive", "Active"],
    "เสี่ยง": ["Risk-taker"],
    "ท้าทาย": ["Risk-taker", "Ambitious"],

    # Caution & Rules
    "ระวัง": ["Cautious", "Conservative"],
    "ตรวจสอบ": ["Detail-oriented", "Precise"],
    "แผน": ["Organized", "Logical"],
    "กฎ": ["Rule-abiding", "Conservative"],
    "เดิม": ["Conservative", "Traditional"],

    # Social vs Solitude
    "เพื่อน": ["Social", "Extrovert"],
    "คุย": ["Social", "Chatty"],
    "คนเดียว": ["Introverted", "Private"],
    "สงบ": ["Introverted", "Calm"],

    # Work Styles
    "ละเอียด": ["Detail-oriented", "Perfectionist"],
    "สร้างสรรค์": ["Creative", "Artistic"],
    "ใหม่": ["Visionary", "Creative"],
    "ผลลัพธ์": ["Ambitious", "Efficient"],
}

# -----------------------------------------------------------------------------
# 4. ANSWER STYLES (สไตล์การตอบตาม Role)
# -----------------------------------------------------------------------------
# ความยาวตัวเลือกที่ชอบ (Long vs Short)
# Formal personas prefer longer answers.
FORMAL_ROLES = ["Manager", "Doctor", "Teacher", "Government Official", "Police Officer", "Civil Engineer", "Start-up Owner"]
INFORMAL_ROLES = ["Student", "Gamer", "YouTuber", "Freelance", "Artist", "Content Creator"]

# -----------------------------------------------------------------------------
# 5. INTERESTS DATABASE (คลังความสนใจใหม่สำหรับ Data Enrichment)
# -----------------------------------------------------------------------------
# เพื่อใช้สุ่ม Generate เพิ่มให้ Persona ถ้าจำเป็น
DEFAULT_INTERESTS = [
    "Technology", "Fashion", "Food", "Travel", "Investment", "Politics", 
    "Health", "Gaming", "Art", "Music", "Reading", "Sports"
]
