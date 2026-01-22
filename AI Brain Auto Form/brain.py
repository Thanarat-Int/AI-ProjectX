import random
import json
import re
import urllib.request
import urllib.error
from faker import Faker
import time
from keyword_weights import (
    AGREEMENT_KEYWORDS, FREQUENCY_KEYWORDS, 
    CONTEXT_KEYWORDS, OPTION_TO_TRAIT,
    FORMAL_ROLES, INFORMAL_ROLES
)
from learning_core import BRAIN_CORE
from data import DATA_MANAGER

class AIBrain:
    def __init__(self):
        pass

    def decide_answer(self, question_text, options, persona, stance_memory=None):
        """
        Main Decision Hub
        """
        # 1. Clean Options
        valid_options = self._filter_valid_options(options, question_text)
        if not valid_options:
            return random.choice(options) if options else ""

        if self._positive_lock_enabled():
            locked_options = self._apply_positive_lock(valid_options)
            if locked_options:
                valid_options = locked_options

        # 1.5 Direct demographic matches (Age / Gender)
        is_age_q = self._is_age_question(question_text) or self._options_look_like_age(valid_options)
        if is_age_q:
            age_choice = self._match_age_option(valid_options, persona.get("age"))
            if age_choice:
                return age_choice

        is_gender_q = self._is_gender_question(question_text) or self._options_look_like_gender(valid_options)
        if is_gender_q:
            gender_choice = self._match_gender_option(valid_options, persona.get("gender"))
            if gender_choice:
                return gender_choice

        # 2. Detect Context (Questions about Work? Life? Money?)
        context = self._detect_context(question_text)
        topic = self._detect_attitude_topic(question_text)
        is_attitude = self._is_attitude_question(question_text, valid_options)
        is_scale = self._is_scale_question(valid_options)
        base_stance = self._get_or_set_stance(topic, question_text, persona, stance_memory, is_scale=is_scale)
        stance = base_stance
        if base_stance is not None and is_attitude and self._is_negative_question(question_text):
            stance = self._invert_stance(base_stance)

        # [GENIUS UPGRADE] Feed Data to Unsupervised Learner
        # The bot learns new vocabulary from every form it sees.
        BRAIN_CORE.feed_data(valid_options)

        # 3. Score Options
        scored_options = []
        for opt in valid_options:
            score, reason = self._calculate_affinity(opt, persona, context, question_text)
            
            # [GENIUS UPGRADE] boost score if it matches a learned cluster?
            # For now, let's just log if it found a cluster
            cid = BRAIN_CORE.predict_category(opt)
            if cid != -1:
                # Experimental: If we knew which cluster the persona liked, we could boost.
                # Currently, just participating in a cluster gives a tiny "Confidence" boost
                # because the bot "knows" this concept.
                score += 0.5 
                reason += f", Known Concept (C{cid})"

            # Consistency boost for attitude questions
            if stance is not None and is_attitude:
                opt_sentiment = self._extract_sentiment(opt)
                if opt_sentiment is None and is_scale:
                    opt_sentiment = self._extract_scale_value(opt)
                if opt_sentiment is not None:
                    score += max(0, 3 - abs(opt_sentiment - stance))
                    reason += f", Stance Align {stance}"

            # Positive lock bias toward 4-5 when enabled
            if self._positive_lock_enabled():
                rating_val = self._extract_rating_value(opt)
                if rating_val is not None and rating_val >= 4:
                    score += 1.5
                    reason += ", Positive Bias 4-5"

            scored_options.append({"text": opt, "score": score, "reason": reason})

        # 4. Select Best Option (Weighted Probabilistic)
        if stance is not None and is_attitude:
            if is_scale:
                forced = self._force_consistent_scale_choice(scored_options, stance)
            else:
                forced = self._force_consistent_choice(scored_options, stance)
            chosen = forced if forced else self._weighted_selection(scored_options)
        else:
            chosen = self._weighted_selection(scored_options)

        if stance_memory is not None and topic and is_attitude:
            key = self._topic_key(topic)
            if key not in stance_memory:
                chosen_sentiment = self._extract_sentiment(chosen.get("text", ""))
                if chosen_sentiment is None and is_scale:
                    chosen_sentiment = self._extract_scale_value(chosen.get("text", ""))
                if chosen_sentiment is not None:
                    stance_memory[key] = chosen_sentiment
        return chosen['text']

    def _get_forbidden_phrases(self):
        phrases = DATA_MANAGER.config.get("forbidden_answers", [])
        if isinstance(phrases, str):
            phrases = [phrases]
        return [p.strip().lower() for p in phrases if p and p.strip()]

    def _get_forbidden_match_mode(self):
        mode = DATA_MANAGER.config.get("forbidden_match_mode", "exact")
        return mode if mode in ["exact", "contains"] else "exact"

    def _normalize_text(self, text):
        return " ".join(text.lower().split())

    def _positive_lock_enabled(self):
        return bool(DATA_MANAGER.config.get("positive_lock"))

    def _extract_binary_value(self, text):
        t = self._normalize_text(text)
        yes_terms = {"yes", "ใช่", "true"}
        no_terms = {"no", "ไม่ใช่", "false"}
        if t in yes_terms:
            return 4
        if t in no_terms:
            return 2
        return None

    def _extract_rating_value(self, text):
        val = self._extract_scale_value(text)
        if val is not None:
            return val
        t = text.lower()
        for k, v in AGREEMENT_KEYWORDS.items():
            if k in t:
                return v
        for k, v in FREQUENCY_KEYWORDS.items():
            if k in t:
                return v
        return self._extract_binary_value(text)

    def _apply_positive_lock(self, options):
        scored = [(opt, self._extract_rating_value(opt)) for opt in options]
        if not any(val is not None for _, val in scored):
            return None
        filtered = [opt for opt, val in scored if val is None or val >= 3]
        return filtered if filtered else None

    def _is_forbidden(self, text, forbidden_phrases):
        text_norm = self._normalize_text(text)
        mode = self._get_forbidden_match_mode()
        if mode == "exact":
            return any(self._normalize_text(p) == text_norm for p in forbidden_phrases)
        return any(self._normalize_text(p) in text_norm for p in forbidden_phrases)

    def filter_options(self, options):
        forbidden = self._get_forbidden_phrases()
        if not forbidden:
            return options
        return [opt for opt in options if not self._is_forbidden(opt, forbidden)]

    def _get_forbidden_age_rules(self):
        rules = DATA_MANAGER.config.get("forbidden_age_rules", []) or []

        # Backward compatibility for explicit age list
        ages = DATA_MANAGER.config.get("forbidden_ages", []) or []
        if isinstance(ages, str):
            ages = [a.strip() for a in ages.split(",")]
        for a in ages:
            try:
                rules.append({"type": "eq", "value": int(a)})
            except Exception:
                continue

        return rules

    def _is_age_question(self, question_text):
        q = question_text.lower()
        if any(k in q for k in ["age", "อายุ", "years old"]):
            return True
        if "ปี" in q and re.search(r"\d{1,3}", q):
            return True
        return False

    def _options_look_like_age(self, options):
        for opt in options:
            t = opt.lower()
            if "ปี" in t or "years" in t:
                return True
            if re.search(r"\d{1,3}\s*[-–]\s*\d{1,3}", t):
                return True
            if re.search(r"\d{1,3}\s*\+", t):
                return True
            nums = self._extract_ages_from_text(t)
            if nums and max(nums) >= 10:
                return True
        return False

    def _is_gender_question(self, question_text):
        q = question_text.lower()
        return any(k in q for k in ["gender", "sex", "เพศ"])

    def _options_look_like_gender(self, options):
        for opt in options:
            if self._extract_gender_from_text(opt):
                return True
        return False

    def _extract_gender_from_text(self, text):
        t = text.lower()
        female_terms = [
            r"\bfemale\b", r"\bwoman\b", r"\bgirl\b",
            "เพศหญิง", "ผู้หญิง", "หญิง"
        ]
        male_terms = [
            r"\bmale\b", r"\bman\b", r"\bboy\b",
            "เพศชาย", "ผู้ชาย", "ชาย"
        ]
        for term in female_terms:
            if re.search(term, t):
                return "female"
        for term in male_terms:
            if re.search(term, t):
                return "male"
        return None

    def _extract_ages_from_text(self, text):
        # Handles "20", "20 ปี", and ranges like "20-25"
        ages = []
        for m in re.findall(r"(\d{1,3})", text):
            try:
                ages.append(int(m))
            except Exception:
                pass
        return ages

    def _text_to_range(self, text):
        t = text.lower()
        range_match = re.search(r"(\d{1,3})\s*[-–]\s*(\d{1,3})", t)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if start > end:
                start, end = end, start
            return start, end

        nums = self._extract_ages_from_text(t)
        if not nums:
            return None
        n = nums[0]

        if any(k in t for k in ["ต่ำกว่า", "น้อยกว่า", "less than", "under", "<"]):
            return 0, n - 1
        if any(k in t for k in ["ขึ้นไป", "มากกว่า", "greater", "over", "above", ">=", ">"]):
            return n, 200

        return n, n

    def _match_age_option(self, options, age):
        try:
            age_val = int(age)
        except Exception:
            return None
        matches = []
        for opt in options:
            rng = self._text_to_range(opt)
            if not rng:
                continue
            min_age, max_age = rng
            if min_age <= age_val <= max_age:
                matches.append(opt)
        if not matches:
            return None
        return random.choice(matches)

    def _match_gender_option(self, options, gender):
        if not gender:
            return None
        g = str(gender).lower()
        if g.startswith("m"):
            target = "male"
        elif g.startswith("f"):
            target = "female"
        else:
            target = g
        matches = []
        for opt in options:
            opt_gender = self._extract_gender_from_text(opt)
            if opt_gender and opt_gender == target:
                matches.append(opt)
        if not matches:
            return None
        return random.choice(matches)

    def _rule_to_range(self, rule):
        r_type = rule.get("type")
        if r_type == "lt":
            return 0, rule.get("value", 0) - 1
        if r_type == "lte":
            return 0, rule.get("value", 0)
        if r_type == "gt":
            return rule.get("value", 0) + 1, 200
        if r_type == "gte":
            return rule.get("value", 0), 200
        if r_type == "range":
            return rule.get("min", 0), rule.get("max", 200)
        if r_type == "eq":
            v = rule.get("value", 0)
            return v, v
        return None

    def _ranges_overlap(self, a_min, a_max, b_min, b_max):
        return not (a_max < b_min or b_max < a_min)

    def _is_forbidden_age_text(self, text, rules):
        option_range = self._text_to_range(text)
        if not option_range:
            return False
        o_min, o_max = option_range
        for rule in rules:
            r_range = self._rule_to_range(rule)
            if not r_range:
                continue
            r_min, r_max = r_range
            if self._ranges_overlap(o_min, o_max, r_min, r_max):
                return True
        return False

    def _age_matches_rules(self, age, rules):
        for rule in rules:
            r_type = rule.get("type")
            if r_type == "lt" and age < rule.get("value", 0):
                return True
            if r_type == "lte" and age <= rule.get("value", 0):
                return True
            if r_type == "gt" and age > rule.get("value", 0):
                return True
            if r_type == "gte" and age >= rule.get("value", 0):
                return True
            if r_type == "range" and rule.get("min", 0) <= age <= rule.get("max", 200):
                return True
            if r_type == "eq" and age == rule.get("value", 0):
                return True
        return False

    def _filter_valid_options(self, options, question_text):
        # Exclude "Other" or text-input fields, plus forbidden phrases
        forbidden = self._get_forbidden_phrases()
        age_rules = self._get_forbidden_age_rules()
        is_scale = self._is_scale_question(options)
        is_age_q = (self._is_age_question(question_text) or self._options_look_like_age(options)) and not is_scale
        return [
            opt for opt in options
            if not any(x in opt.lower() for x in ["other", "อื่น", "ระบุ"])
            and not self._is_forbidden(opt, forbidden)
            and not (
                is_age_q
                and age_rules
                and self._is_forbidden_age_text(opt, age_rules)
            )
        ]

    def filter_choice_options(self, question_text, options):
        return self._filter_valid_options(options, question_text)

    def _detect_context(self, question_text):
        q_lower = question_text.lower()
        found_contexts = []
        for ctx, keywords in CONTEXT_KEYWORDS.items():
            if any(k in q_lower for k in keywords):
                found_contexts.append(ctx)
        return found_contexts

    def _detect_attitude_topic(self, question_text):
        q = question_text.lower()
        topic_map = {
            "wfh": ["wfh", "work from home", "ทำงานที่บ้าน", "remote", "ทางไกล"],
            "organization": ["องค์กร", "บริษัท", "ที่ทำงาน", "องค์กรนี้", "company", "organization"],
            "work": ["งาน", "job", "work", "ภาระงาน"],
            "manager": ["หัวหน้า", "manager", "lead", "ผู้จัดการ"],
            "benefits": ["สวัสดิการ", "benefit", "ค่าตอบแทน", "เงินเดือน", "salary"],
            "culture": ["วัฒนธรรม", "culture", "ทีม", "บรรยากาศ"],
            "happiness": ["มีความสุข", "พอใจ", "satisfied", "happy", "enjoy", "รัก", "ชอบ"],
        }
        for topic, keys in topic_map.items():
            if any(k in q for k in keys):
                return topic
        return None

    def _topic_key(self, topic):
        if not topic:
            return None
        work_topics = {"wfh", "organization", "work", "manager", "benefits", "culture", "happiness"}
        if topic in work_topics:
            return "work_core"
        return topic

    def _has_attitude_keywords(self, question_text):
        q = question_text.lower()
        keywords = [
            "ชอบ", "รัก", "พอใจ", "มีความสุข", "ภูมิใจ", "ผูกพัน",
            "ทุ่มเท", "ตั้งใจ", "ความหมาย", "อยากอยู่", "ต้องการอยู่",
            "เห็นด้วย", "ไม่เห็นด้วย", "รู้สึก", "คิดเห็น", "เชื่อว่า",
            "มองว่า", "คิดว่า", "ยินดี", "พร้อม", "loyal", "proud",
            "engage", "belong", "commit", "satisfied", "happy", "enjoy",
            "agree", "disagree"
        ]
        return any(k in q for k in keywords)

    def _is_attitude_question(self, question_text, options):
        if self._detect_attitude_topic(question_text):
            return True
        if self._has_attitude_keywords(question_text):
            return True
        for opt in options:
            if self._extract_sentiment(opt) is not None:
                return True
        if self._is_scale_question(options):
            return True
        return False

    def _is_negative_question(self, question_text):
        q = question_text.lower()
        neg_terms = [
            "ไม่", "ไม่ได้", "ไม่เคย", "ไม่มี", "ไม่ค่อย", "ไม่รู้สึก",
            "ไม่ต้องการ", "ไม่อยาก", "not", "never", "hardly", "rarely", "no longer"
        ]
        return any(t in q for t in neg_terms)

    def _invert_stance(self, stance, max_val=5):
        try:
            val = int(stance)
        except Exception:
            return stance
        return max_val + 1 - val

    def _is_scale_question(self, options):
        vals = [self._extract_scale_value(o) for o in options]
        vals = [v for v in vals if v is not None]
        if len(vals) < 3:
            return False
        return 1 <= min(vals) and max(vals) <= 10

    def _extract_scale_value(self, option_text):
        nums = re.findall(r"\d{1,2}", option_text)
        if not nums:
            return None
        try:
            val = int(nums[0])
        except Exception:
            return None
        return val if 1 <= val <= 10 else None

    def _extract_sentiment(self, option_text):
        opt_lower = option_text.lower()
        for k, v in AGREEMENT_KEYWORDS.items():
            if k in opt_lower:
                return v
        return None

    def _get_or_set_stance(self, topic, question_text, persona, stance_memory, is_scale=False):
        if not topic or stance_memory is None:
            return None
        key = self._topic_key(topic)
        if key in stance_memory:
            return stance_memory[key]
        stance = self._initial_stance(topic, question_text, persona)
        if is_scale:
            stance = self._scale_base_stance(stance)
        if stance is not None:
            stance_memory[key] = stance
        return stance

    def _initial_stance(self, topic, question_text, persona):
        q = question_text.lower()
        values = [v.lower() for v in persona.get("values", [])]
        personality = persona.get("personality", "").lower()
        interests = [i.lower() for i in persona.get("interests", [])]

        if any(v in q for v in values):
            return 4

        if any(t in personality for t in ["optimistic", "energetic", "friendly"]):
            return 4
        if any(t in personality for t in ["stressed", "skeptical", "cautious", "serious"]):
            return 2

        if topic == "wfh":
            if any(t in personality for t in ["introverted", "calm", "quiet"]):
                return 4
            if any(t in personality for t in ["extroverted", "social", "outgoing"]):
                return 2
            if "freedom" in values or "flexibility" in values:
                return 4
            if "teamwork" in interests or "social" in interests:
                return 2

        return 3

    def _force_consistent_choice(self, scored_options, stance):
        if stance >= 4:
            target = "pos"
        elif stance <= 2:
            target = "neg"
        else:
            target = "neu"

        filtered = []
        for item in scored_options:
            opt_sentiment = self._extract_sentiment(item.get("text", ""))
            if opt_sentiment is None:
                continue
            if target == "pos" and opt_sentiment >= 4:
                filtered.append(item)
            elif target == "neg" and opt_sentiment <= 2:
                filtered.append(item)
            elif target == "neu" and opt_sentiment == 3:
                filtered.append(item)

        if not filtered:
            return None
        return self._weighted_selection(filtered)

    def _force_consistent_scale_choice(self, scored_options, stance):
        target = self._clamp_scale(stance + random.choice([-1, 0, 1]))
        best = []
        best_diff = 999
        for item in scored_options:
            val = self._extract_scale_value(item.get("text", ""))
            if val is None:
                continue
            diff = abs(val - target)
            if diff < best_diff:
                best = [item]
                best_diff = diff
            elif diff == best_diff:
                best.append(item)
        if not best:
            return None
        return self._weighted_selection(best)

    def _clamp_scale(self, value, min_val=1, max_val=5):
        try:
            val = int(value)
        except Exception:
            return min_val
        return max(min_val, min(max_val, val))

    def _scale_base_stance(self, stance):
        if stance is None:
            return None
        return self._clamp_scale(stance + random.choice([-1, 0, 1]))

    def _calculate_affinity(self, option_text, persona, context_list, question_text):
        """
        Core Logic: Calculates how much this option matches the persona.
        Base Score = 0
        """
        score = 0
        opt_lower = option_text.lower()
        reason = []

        # --- A. Interest Match (High Impact) ---
        # If the option mentions something the persona is interested in.
        # e.g. Persona likes "Technology" and option is "Use App"
        for interest in persona.get('interests', []):
            if interest in CONTEXT_KEYWORDS:
                # Check keywords associated with this interest
                for keyword in CONTEXT_KEYWORDS[interest]:
                    if keyword in opt_lower:
                        score += 3
                        reason.append(f"Interest '{interest}' match")
                        break

        # --- B. Trait Alignment (Medium Impact) ---
        # Map option to specific traits
        for key_word, associated_traits in OPTION_TO_TRAIT.items():
            if key_word in opt_lower:
                # Check if persona has these traits
                p_traits = [t.lower() for t in persona['personality'].split(", ")]
                for trait in associated_traits:
                    if trait.lower() in p_traits:
                        score += 2
                        reason.append(f"Trait '{trait}' match")
                    else:
                        # Slight penalty if completely opposite traits exist (simplified)
                        pass

        # --- C. Role/Style Alignment (Low Impact) ---
        # Formal roles ignore informal language, etc.
        # Length Preference
        if persona['role'] in FORMAL_ROLES:
            if len(option_text) > 20: # Prefer longer, detailed answers
                score += 1
                reason.append("Formal Role prefers detail")
        elif persona['role'] in INFORMAL_ROLES:
             if len(option_text) < 15: # Prefer short answers
                score += 1
                reason.append("Informal Role prefers brief")

        # --- D. Scale Logic (Agree/Disagree) ---
        # If it's a Likert scale (Agree <-> Disagree)
        # We need to see if the QUESTION aligns with persona's VALUES.
        is_scale = any(k in opt_lower for k in AGREEMENT_KEYWORDS)
        if is_scale:
            # Check if Question matches Values
            q_matches_values = False
            for val in persona.get('values', []):
                 if val.lower() in question_text.lower():
                     q_matches_values = True
                     break
            
            # Determine sentiment of the option
            opt_sentiment = 3 # Neutral
            for k, v in AGREEMENT_KEYWORDS.items():
                if k in opt_lower:
                    opt_sentiment = v
                    break
            
            if q_matches_values:
                # If they value this topic, they tend to "Agree" (Score 4-5)
                if opt_sentiment >= 4: return scale_boost(score + 3, reason, "Values match -> Agree")
                if opt_sentiment <= 2: return scale_boost(score - 2, reason, "Values match -> Disagree Conflict")
            
        return score, ",".join(reason)

    def _weighted_selection(self, scored_options):
        """
        Pick an option based on scores.
        Higher score = Higher chance, but not 100% deterministic (to allow variety).
        """
        # 1. Sort by score
        scored_options.sort(key=lambda x: x['score'], reverse=True)

        if not scored_options:
            return {"text": ""} # Should not happen

        # 2. Get Top Candidates (let's say Top 3 or all with score > X)
        # Logic: Convert score to weight.
        # Weight = 2^(score). Example: Score 3 -> 8, Score 1 -> 2.
        
        candidates = []
        weights = []
        
        min_score = min(s['score'] for s in scored_options)
        
        for item in scored_options:
            # Shift scores to be positive for weighting
            adjusted_score = item['score'] - min_score 
            weight = (1.5 ** adjusted_score) # Exponential weight
            candidates.append(item)
            weights.append(weight)

        # 3. Random Pick
        chosen = random.choices(candidates, weights=weights, k=1)[0]
        return chosen

    def decide_text_input(self, question_text, persona, use_faker=False):
        """
        Decides what to type in text fields.
        Supports Faker for identity fields if enabled.
        """
        age_rules = self._get_forbidden_age_rules()
        if self._is_age_question(question_text) and self._age_matches_rules(persona.get("age", 0), age_rules):
            return None
        if use_faker:
            fake = Faker('th_TH')
            q_lower = question_text.lower()
            
            # Identity Heuristics
            if any(x in q_lower for x in ["email", "อีเมล", "e-mail"]):
                # Generate realistic email based on persona
                user = persona.get('name', 'user').lower().replace(" ", ".")
                return f"{user}.{random.randint(10,99)}@gmail.com"
            
            if any(x in q_lower for x in ["phone", "เบอร์", "โทร", "mobile"]):
                return f"0{random.randint(8,9)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
            
            if any(x in q_lower for x in ["name", "ชื่อ", "full name"]):
                if "first" in q_lower or "ชื่อจริง" in q_lower:
                    return persona.get('name')
                return f"{persona.get('name')} {fake.last_name()}"
            
            if any(x in q_lower for x in ["address", "ที่อยู่", "addr"]):
                return fake.address().replace("\n", " ")

        # [FUTURE UPGRADE] LLM Integration Layer
        # Checks config.json for 'llm_api_key'
        llm_key = DATA_MANAGER.config.get("llm_api_key", "")
        
        if llm_key and "YOUR_API_KEY" not in llm_key and len(llm_key) > 10:
             try:
                 return self._ask_gemini(question_text, persona, llm_key)
             except Exception as e:
                 print(f"LLM Error: {e}")
                 # Fallback to None (heuristic)
                 pass

        return None

    def _ask_gemini(self, question, persona, api_key):
        """
        Lightweight REST call to Gemini Flash (No pip install needed)
        """
        model = "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        prompt = f"""
        Act as this persona:
        Name: {persona['name']}
        Role: {persona['role']}
        Traits: {persona['personality']}
        
        Task: Answer this form question briefly and realistically.
        Question: "{question}"
        Answer:
        """
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.9,
                "maxOutputTokens": 100
            }
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            answer = result['candidates'][0]['content']['parts'][0]['text']
            return answer.strip()

def scale_boost(score, reason_list, msg):
    reason_list.append(msg)
    return score, ",".join(reason_list)
