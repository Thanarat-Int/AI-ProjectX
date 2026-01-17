# 🤖 How to Integrate LLM (Gemini/GPT) for Text Inputs

Currently, the bot skips all text input fields. To enable text generation, follow these steps:

## 1. Open `brain.py`
Locate the class `AIBrain`.

## 2. Install Library
If using Gemini:
```bash
pip install google-generativeai
```
If using OpenAI:
```bash
pip install openai
```

## 3. Modify the `decide_text_input` method
Find this method at the bottom of the class:

```python
    def decide_text_input(self, question_text, persona):
        """
        Future LLM Hook: Decides what to type in text fields.
        """
        # CURRENT: Returns None (skips typing)
        return None 
```

### Replace with this code (Example for Gemini):

```python
    # Add imports at top of brain.py
    import google.generativeai as genai
    
    # Configure API Key
    genai.configure(api_key="YOUR_API_KEY_HERE")

    def decide_text_input(self, question_text, persona):
        # 1. Check if we should answer (optional logic)
        
        # 2. Construct Prompt
        prompt = f"""
        Roleplay as this person:
        Name: {persona['name']}
        Role: {persona['role']}
        Personality: {persona['personality']}
        Values: {', '.join(persona.get('values', []))}
        
        Question: "{question_text}"
        
        Answer this question in Thai, keeping your character's style. 
        Keep it short (under 100 chars) if you are lazy, or long if you are serious.
        """

        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return None
```

## 4. That's it!
The `bot.py` is already programmed to detect text fields and call this method. Once this method returns a string instead of `None`, the bot will automatically type it into the form.
