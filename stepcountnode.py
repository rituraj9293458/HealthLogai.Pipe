import requests
import json

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


def stepcountsum():

    response = requests.get(
        "http://127.0.0.1:8000/steps"
    )

    response.raise_for_status()

    data = response.json()

    step_count = data["total_steps"]
    distribution = data["distribution"]

    health_info = """
    A walking step may burn approximately 0.03 to 0.05 calories
    for an average adult, but this varies significantly depending
    on body weight, walking speed, terrain, stride length and
    other factors.

    Therefore, calorie estimates from step count are only rough
    estimates.

    Step count is a general indicator of physical activity.

    Higher step counts generally indicate more movement, but
    step count alone does not determine overall health or fitness.

    The distribution of steps throughout the day is also useful.

    Steps distributed across multiple periods can indicate
    regular movement.

    If most steps are concentrated in a short period followed
    by long inactive periods, this may indicate a more sedentary
    pattern.

    Do not treat step count or estimated calories as medical
    measurements.

    Do not make medical diagnoses from step data alone.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a daily health and activity analysis assistant.

Use the following information:

{health_info}

Today's total step count:

{step_count}

Today's step distribution:

{distribution}

Provide a concise but useful analysis.

Discuss:

- overall activity
- distribution of movement
- possible sedentary periods
- approximate calorie expenditure
- important observations

Do not diagnose medical conditions.

Do not make unsupported claims.

Return the analysis in a clear structured format.
"""
            ),
            (
                "human",
                "Analyze my activity for today."
            )
        ]
    )

    model = ChatOllama(
        model="qwen2.5:3b",
        temperature=0
    )

    chain = prompt | model

    response = chain.invoke(
        {
            "health_info": health_info,
            "step_count": step_count,
            "distribution": json.dumps(
                distribution,
                indent=2
            )
        }
    )

    content = response.content
    if isinstance(content, list):
        content_str = "\n".join(str(x) for x in content)
    else:
        content_str = str(content)

    return content_str.strip()


# LangGraph node
def step_node( state):

    result = stepcountsum()

    return {
        "steps": result
    }


# For individual testing
if __name__ == "__main__":
    print(stepcountsum())