import streamlit as st

from llm import chat_with_llm
from token_utils import count_message_tokens
from memory_manager import save_memory, retrieve_memories


st.set_page_config(
    page_title="Adaptive Memory AI",
    page_icon="🧠"
)

st.title("🧠 Adaptive Long-Term Memory AI")
st.write("Demo chatbot có bộ nhớ dài hạn thích ứng.")


WINDOW_SIZE = 4


# =========================
# SESSION
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================
# HIỂN THỊ CHAT
# =========================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# =========================
# TOKEN STATISTICS
# =========================

full_history_tokens = count_message_tokens(
    st.session_state.messages
)

recent_messages = st.session_state.messages[-WINDOW_SIZE:]

window_tokens = count_message_tokens(
    recent_messages
)

if full_history_tokens > 0:
    reduction_percent = (
        (full_history_tokens - window_tokens)
        / full_history_tokens
        * 100
    )
else:
    reduction_percent = 0


st.sidebar.title("📊 Memory Statistics")

st.sidebar.metric(
    "Full history tokens",
    full_history_tokens
)

st.sidebar.metric(
    "Sliding window tokens",
    window_tokens
)

st.sidebar.metric(
    "Messages",
    len(st.session_state.messages)
)

st.sidebar.metric(
    "Token reduction",
    f"{reduction_percent:.1f}%"
)


# =========================
# CHAT INPUT
# =========================

user_input = st.chat_input("Nhập tin nhắn...")


if user_input:

    # 1. Lưu user message vào session
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    # =========================
    # 2. MEMORY STORAGE
    # =========================

    text_lower = user_input.lower()

    memory_keywords = [
        "mình tên",
        "tôi tên",
        "mình thích",
        "tôi thích",
        "mình đang học",
        "tôi đang học",
        "mình làm",
        "tôi làm",
        "mình dùng",
        "tôi dùng"
    ]

    should_save = any(
        keyword in text_lower
        for keyword in memory_keywords
    )

    if should_save:
        save_memory(
            user_input,
            category="profile",
            importance=1.0
        )

    # =========================
    # 3. RETRIEVE MEMORY
    # =========================

    relevant_memories = retrieve_memories(
        user_input,
        n_results=3
    )

    # =========================
    # 4. SLIDING WINDOW
    # =========================

    recent_messages = st.session_state.messages[-WINDOW_SIZE:]

    # =========================
    # 5. GỌI QWEN
    # =========================

    with st.spinner("AI đang suy nghĩ..."):

        assistant_response = chat_with_llm(
            recent_messages,
            memories=relevant_memories
        )

    # =========================
    # 6. LƯU ASSISTANT RESPONSE
    # =========================

    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_response
    })

    with st.chat_message("assistant"):
        st.write(assistant_response)

    st.rerun()