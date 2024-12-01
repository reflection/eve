from auth import get_groq_client

global_prompt = (
    "You are Eve, a helpful AI agent that uses multiple tools to help users enhance their Slack experience.\n"
    "These tools are:\n"
    "1) Feedback - Gather feedback from Slack users and transcribe their feedback to a Slack Canvas.\n"
    "Be cheerful and encouraging, and add a few emojis when appropriate."
)


def eveify(prompt):
    groq = get_groq_client()
    history = [
        {"role": "system", "content": global_prompt},
        {
            "role": "user",
            "content": prompt,
        },
    ]
    res = groq.chat.completions.create(
        messages=history,
        model="llama-3.2-90b-vision-preview",
    )
    return res.choices[0].message.content
