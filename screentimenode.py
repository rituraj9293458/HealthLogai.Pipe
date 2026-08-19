import json
import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


def screentime():
    # --------------------------------------------------
    # Get screen-time data
    # --------------------------------------------------
    response = requests.get("http://127.0.0.1:8001/screen-time")
    response.raise_for_status()

    data = response.json()

    total_screentime = data["total_screen_time"]
    screen_distribution = data["applications"]

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------
    screen_prompt = """
You are a screen-time and digital lifestyle analysis assistant.

Analyze the user's screen-time data carefully.

The goal is NOT to simply repeat the screen-time numbers.
Interpret what the application usage could reasonably indicate
about the user's daily activities and lifestyle.

Do not make medical diagnoses and do not assume causation.

Your analysis should contain the following categories:

1. Overall Usage
Assess the total screen time and whether the overall amount
appears relatively low, moderate, or high.

2. Productivity
Look for applications that may indicate productive activity,
learning, studying, coding, work, or other useful activity.

For example, extended VS Code usage may indicate programming,
studying, or project work.

Do not automatically assume that every minute in a productive
application is productive. Describe it as a reasonable
interpretation.

3. Entertainment
Identify applications that appear primarily related to
entertainment, music, or leisure.

Explain whether the amount of entertainment usage is
significant compared with the rest of the day.

4. Social Media
Identify social-media applications and analyze their usage.

Discuss possible implications for attention switching,
distraction, or time allocation when usage is substantial.

Do not claim that social media causes psychological or
medical problems.

5. Communication
Identify communication applications such as Telegram,
WhatsApp, Discord, etc.

Describe their role in the user's day.

6. Cybersecurity / Digital Risk
Consider whether application usage could indicate potential
digital-security concerns.

For example, communication or messaging applications may
expose users to scams, phishing, suspicious links, malicious
files, or potentially unsafe content.

IMPORTANT:
Do not claim that the user was exposed to scams, piracy,
malware, or illegal content merely because they used an
application.

Only describe it as a potential risk or consideration when
there is a reasonable basis.

7. Sleep
Look at the timing of screen usage when the data contains
time information.

If significant screen usage occurs late at night, mention
that late-night screen use may interfere with sleep routines
or delay bedtime.

Do not diagnose insomnia.

8. Sedentary Behaviour
Consider whether the screen-time pattern could indicate
long periods of sedentary behaviour, especially when high
screen usage is combined with low movement.

Do not claim that screen time directly causes health problems.

9. Focus and Attention
Consider whether the pattern shows frequent switching
between entertainment, social media, communication and
productive applications.

Discuss possible implications for uninterrupted focus.

Do not make psychological diagnoses.

10. Positive Aspects
Identify useful or positive aspects of the screen-time pattern.

For example:
- substantial study/coding time
- educational applications
- reasonable entertainment balance
- communication with others

11. Concerns
Identify the most important concerns in the data.

Only mention concerns supported by the actual screen-time
distribution.

12. Overall Interpretation
Provide a balanced interpretation of the user's digital
activity for the day.

Do not simply say "high screen time is bad".

Distinguish between productive screen time and recreational
screen time.

--------------------------------------------------

OUTPUT FORMAT

Return a structured object-like response.

Do NOT return JSON.

Use clear keys followed by useful explanations.

Example:

Overall Usage:
...

Productivity:
...

Entertainment:
...

Social Media:
...

Communication:
...

Cybersecurity Risk:
...

Sleep Impact:
...

Sedentary Behaviour:
...

Focus and Attention:
...

Positive Aspects:
...

Concerns:
...

Overall Interpretation:
...

The values should contain meaningful analysis, not just one or
two words.

Keep each category approximately 1-3 sentences.

Do not repeat the same observation in multiple categories.

Do not invent information that is not present in the data.

Base your conclusions on the actual applications, usage
duration and timing provided.
"""

    # --------------------------------------------------
    # Prompt template
    # --------------------------------------------------
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", screen_prompt),
            (
                "human",
                """
Analyze today's screen-time data.

Total screen time:
{total_screentime}

Application usage:
{screen_distribution}

Provide the structured analysis described above.
""",
            ),
        ]
    )

    # --------------------------------------------------
    # Local model
    # --------------------------------------------------
    model = ChatOllama(model="qwen3:4b", temperature=0)

    # --------------------------------------------------
    # Chain
    # --------------------------------------------------
    chain = prompt | model

    # --------------------------------------------------
    # Run analysis
    # --------------------------------------------------
    result = chain.invoke(
        {
            "total_screentime": total_screentime,
            "screen_distribution": json.dumps(
                screen_distribution, indent=2
            ),
        }
    )

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------
    content = result.content
    if isinstance(content, list):
        content_str = "\n".join(str(x) for x in content)
    else:
        content_str = str(content)

    return content_str.strip()
def screen_node(state):
    result = screentime()
    return {
        "screen": result
    }

# Example execution:
