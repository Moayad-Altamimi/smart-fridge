try:
    from groq import Groq
except ImportError:
    Groq = None

import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_recipe(items, meal_type):  
    inventory_text = ", ".join(
        f"{name} ({info['qty']} {info.get('unit', 'pcs')})"
        if isinstance(info, dict)
        else f"{name} ({info})"
        for name, info in items.items()
    )

    # FIX: Return error if inventory is empty
    if not inventory_text or not items:
        return "❌ Cannot generate recipe: Your inventory is empty! Add some items first."

    prompt = (
        f"Create a SHORT and QUICK {meal_type} recipe using: {inventory_text}. "
        "Format the response as Title, Ingredients (bullet list), Steps (numbered, 4-5 steps only). "
        "Make it practical for daily use."
    )

    if not Groq:
        return "Recipe generation is unavailable because the AI library is not installed."

    try:
        client = Groq(api_key=GROQ_API_KEY)
        message = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=300,
        )
        return message.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}