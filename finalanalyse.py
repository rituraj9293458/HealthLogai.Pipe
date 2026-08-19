import json
import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# Final analysis prompt
# --------------------------------------------------

final_prompt = """
You are the final daily health and lifestyle analysis assistant.

You will receive a complete daily health record retrieved
from a database.

The record contains:

- physical activity
- screen time
- food and nutrition

Analyze the information together.

Do NOT simply repeat the individual analyses.

Look for meaningful relationships between:

- physical activity and screen time
- physical activity and diet
- screen time and sedentary behaviour
- screen time and sleep considerations
- food intake and activity
- productive versus recreational screen usage
- overall balance of the day

Only make relationships that are reasonably supported by
the provided information.

Do not diagnose medical conditions.

Do not claim that one behaviour directly caused another.

Use cautious language such as:

"may contribute"
"could be associated with"
"may suggest"
"could be worth considering"

Create a comprehensive daily report.

Use this structure:

DAILY HEALTH REPORT

1. EXECUTIVE SUMMARY

Provide an overview of the user's day.

2. PHYSICAL ACTIVITY

Discuss step count, movement distribution and sedentary
periods.

3. SCREEN TIME AND DIGITAL BEHAVIOUR

Discuss total screen time, productivity, entertainment,
social media, communication, focus and cybersecurity
considerations.

4. NUTRITION

Discuss food intake, nutritional quality, allergens and
important dietary patterns.

5. RELATIONSHIPS BETWEEN BEHAVIOURS

Correlate the three areas where appropriate.

6. POSITIVE ASPECTS

Identify the strongest positive aspects of the day.

7. AREAS OF CONCERN

Identify the most important concerns.

8. RECOMMENDATIONS

Provide practical recommendations based on the data.

9. OVERALL ASSESSMENT

Give a balanced final assessment.

Do not invent information.

Do not diagnose medical conditions.

Return only the final report.
"""


# --------------------------------------------------
# Prompt
# --------------------------------------------------

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            final_prompt
        ),
        (
            "human",
            """
Here is the complete daily record retrieved from the database:

{db_data}

Analyze the complete record and produce the final report.
"""
        )
    ]
)


# --------------------------------------------------
# Gemini model
# --------------------------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)


# --------------------------------------------------
# Chain
# --------------------------------------------------

chain = prompt | model


# --------------------------------------------------
# LangGraph node
# --------------------------------------------------

def final_node(state):

    result = chain.invoke(
        {
            "db_data": json.dumps(
                state["db_data"],
                indent=2,
                default=str
            )
        }
    )

    content = result.content
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            else:
                text_parts.append(str(part))
        final_text = "\n".join(text_parts)
    else:
        final_text = str(content)

    return {
        "final_analysis": final_text.strip()
    }