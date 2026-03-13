from openai import OpenAI
from app.config import OPENAI_API_KEY
from typing import Optional

client = OpenAI(api_key=OPENAI_API_KEY)

def chat_with_ai(
    message: str,
    history: list[dict],
    document_context: Optional[str] = None
) -> str:
    system_prompt = "You are a helpful assistant."

    if document_context:
        system_prompt = f"""You are a helpful assistant that answers questions based on the provided document.

Document content:
{document_context[:4000]}

Answer questions based on this document. If the answer is not in the document, say so."""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return response.choices[0].message.content