from brain import AIBrain
from data import DATA_MANAGER
PERSONAS = DATA_MANAGER.personas

def test_brain():
    brain = AIBrain()
    
    # Test Case 1: Tech question for a Tech Savvy persona
    print("\n--- Test Case 1: Tech Question ---")
    persona_tech = next(p for p in PERSONAS if p['name'] == "Bank") # Programmer
    question = "How do you solve problems?"
    options = ["Use technology and code", "Ask a friend", "Guess"]
    
    choice = brain.decide_answer(question, options, persona_tech)
    print(f"Persona: {persona_tech['name']} ({persona_tech['role']})")
    print(f"Question: {question}")
    print(f"Options: {options}")
    print(f"Chosen: {choice}")
    
    # Test Case 2: Social question for Introvert vs Extrovert
    print("\n--- Test Case 2: Social Question ---")
    question_social = "What do you do on weekends?"
    options_social = ["Go to a party", "Stay home and read", "Work overtime"]
    
    # Introvert
    persona_intro = next(p for p in PERSONAS if p['name'] == "Bank")
    choice_intro = brain.decide_answer(question_social, options_social, persona_intro)
    
    # Extrovert (May)
    persona_extro = next(p for p in PERSONAS if p['name'] == "May")
    choice_extro = brain.decide_answer(question_social, options_social, persona_extro)
    
    print(f"Question: {question_social}")
    print(f"Introvert ({persona_intro['name']}) chose: {choice_intro}")
    print(f"Extrovert ({persona_extro['name']}) chose: {choice_extro}")

    # Test Case 3: Formal vs Informal
    print("\n--- Test Case 3: Length/Formal Preference ---")
    persona_manager = next(p for p in PERSONAS if p['name'] == "Prasit")
    question_plan = "Describe your business plan."
    options_plan = ["Good.", "It is a very detailed and structured plan for long-term growth."]
    
    choice_mgr = brain.decide_answer(question_plan, options_plan, persona_manager)
    print(f"Manager ({persona_manager['name']}) chose: {choice_mgr}")

if __name__ == "__main__":
    test_brain()
