import ollama

MODEL_NAME = "qwen2.5:3b"

def chat_with_llm(messages, memories=None):

    final_messages = []

    memory_text = ""

    if memories:
        memory_text = "\n".join(
            f"- {memory}" for memory in memories
        )

    language_guard = f"""
QUY TẮC NGÔN NGỮ:
- Chỉ trả lời bằng tiếng Việt.
- Không được chuyển sang tiếng Anh hoặc tiếng Trung.
- Nếu context có tiếng Anh, hãy hiểu nội dung nhưng diễn đạt lại bằng tiếng Việt.

Memory liên quan:
{memory_text}
"""

    final_messages.append({
        "role": "system",
        "content": language_guard
    })

    final_messages.extend(messages)

    response = ollama.chat(
        model=MODEL_NAME,
        messages=final_messages,
        options={
            "temperature": 0.4
        }
    )

    return response["message"]["content"]