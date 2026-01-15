import random
import json
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

    def decide_answer(self, question_text, options, persona):
        """
        Main Decision Hub
        """
        # 1. Clean Options
        valid_options = self._filter_valid_options(options)
        if not valid_options:
            return random.choice(options) if options else ""

        # 2. Detect Context (Questions about Work? Life? Money?)
        context = self._detect_context(question_text)

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

            scored_options.append({"text": opt, "score": score, "reason": reason})

        # 4. Select Best Option (Weighted Probabilistic)
        chosen = self._weighted_selection(scored_options)
        return chosen['text']

    def _filter_valid_options(self, options):
        # Exclude "Other" or text-input fields
        return [opt for opt in options 
                if not any(x in opt.lower() for x in ["other", "อื่น", "ระบุ"])]

    def _detect_context(self, question_text):
        q_lower = question_text.lower()
        found_contexts = []
        for ctx, keywords in CONTEXT_KEYWORDS.items():
            if any(k in q_lower for k in keywords):
                found_contexts.append(ctx)
        return found_contexts

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