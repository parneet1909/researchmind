import os
from langchain_mistralai import ChatMistralAI


def generate_chat_title(topic, api_key):

    llm = ChatMistralAI(
        model="ministral-3b-latest",
        temperature=0.2,
        mistral_api_key=api_key
    )

    prompt = f"""
    Generate a very short AI chat title.

    Rules:
    - Maximum 4 or 5 words
    - Professional
    - Clean and optimized
    - No quotes
    - No punctuation at end
    - Summarize the topic clearly

    Topic:
    {topic}
    """

    try:

        response = llm.invoke(prompt)

        title = response.content.strip()

        # EXTRA SAFETY
        words = title.split()

        if len(words) > 6:
            title = " ".join(words[:6])

        return title

    except Exception:

        # fallback
        return topic[:40]