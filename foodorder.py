import json
import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


def foodordersum():
    # --------------------------------------------------
    # Get food-order data from local food app
    # --------------------------------------------------
    response = requests.get("http://127.0.0.1:8002/food")
    response.raise_for_status()

    data = response.json()

    # --------------------------------------------------
    # Group orders by meal period
    # --------------------------------------------------
    breakfast = []
    snacks = []
    lunch = []
    dinner = []

    for order in data["orders"]:
        item_data = {"item": order["item"], "quantity": order["quantity"]}

        meal_period = order["meal_period"]

        if meal_period == "breakfast":
            breakfast.append(item_data)
        elif meal_period == "snack":
            snacks.append(item_data)
        elif meal_period == "lunch":
            lunch.append(item_data)
        elif meal_period == "dinner":
            dinner.append(item_data)

    final = {
        "breakfast": breakfast,
        "snacks": snacks,
        "lunch": lunch,
        "dinner": dinner,
    }

    # --------------------------------------------------
    # Food analysis instructions
    # --------------------------------------------------
    food_prompt = """
Analyze these food orders.

For each food provide:

Food + quantity
Ingredients
Approximate nutrition:
- calories
- protein
- carbs
- fat
- fiber
- sodium

Potential allergens based only on ingredients that are
actually typical or reasonably possible for the dish.

Health considerations:
Mention important nutritional characteristics such as
high fat, sodium, sugar, calories, protein or fiber.

Do not make medical diagnoses.
Do not claim a food directly causes a disease.
Use "may", "could", or "when consumed frequently" for
health effects.

At the end provide:

Daily Nutrition:
- calories
- protein
- carbs
- fat
- fiber
- sodium

Daily Assessment:
- positive aspects
- main concerns
- overall dietary pattern

Keep the output structured and informative but concise.
Do not use JSON.
Do not use Markdown code blocks.
"""

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", food_prompt),
            (
                "human",
                """
Analyze the following food orders.

Food orders:

{food_orders}

Follow the exact organizational structure specified in the
instructions.
""",
            ),
        ]
    )

    # --------------------------------------------------
    # Local model
    # --------------------------------------------------
    model = ChatOllama(model="medgemma1.5", temperature=0)

    # --------------------------------------------------
    # Chain
    # --------------------------------------------------
    chain = prompt | model

    # --------------------------------------------------
    # Run analysis
    # --------------------------------------------------
    response = chain.invoke(
        {"food_orders": json.dumps(final, indent=2)}
    )

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------
    content = response.content
    if isinstance(content, list):
        content_str = "\n".join(str(x) for x in content)
    else:
        content_str = str(content)

    return content_str.strip()
def food_node(state):
    result = foodordersum()
    return {
        "food": result
    }

# Example execution:
if __name__ == "__main__":
    summary = foodordersum()
    print(summary)