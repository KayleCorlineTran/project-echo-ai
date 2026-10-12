import os
import streamlit as st

from game_state import GameState
from puzzle_manager import (
    inspect_object,
    use_code,
    move_room
)


st.set_page_config(
    page_title="PROJECT ECHO",
    page_icon="🔴",
    layout="wide"
)


# =========================
# KHỞI TẠO GAME
# =========================

if "game" not in st.session_state:
    st.session_state.game = GameState()

if "game_log" not in st.session_state:
    st.session_state.game_log = [
        "Bạn tỉnh dậy trong một phòng thí nghiệm tối om."
    ]


game = st.session_state.game


# =========================
# ROOM IMAGES
# =========================

room_images = {
    "laboratory": "assets/laboratory.png",
    "library": "assets/library.png",
    "generator": "assets/generator_room.png",
    "control": "assets/control_room.png"
}


# =========================
# TITLE
# =========================

st.title("🔴 PROJECT ECHO")
st.caption(
    "Memory-Aware Generative AI Escape Room"
)


# =========================
# MAIN LAYOUT
# =========================

left, right = st.columns(
    [3, 1],
    gap="large"
)


# =========================
# LEFT: GAME WORLD
# =========================

with left:

    st.subheader(
        f"📍 Current Room: {game.current_room.upper()}"
    )

    image_path = room_images.get(
        game.current_room
    )

    if image_path and os.path.exists(image_path):
        st.image(
            image_path,
            use_container_width=True
        )

    else:
        st.info(
            "Chưa có ảnh cho căn phòng này."
        )


    # =========================
    # GAME LOG
    # =========================

    st.subheader("📖 Story")

    for message in st.session_state.game_log[-6:]:
        st.write(message)


    # =========================
    # ACTIONS
    # =========================

    st.subheader("🎮 Actions")

    action_tab, code_tab, move_tab = st.tabs([
        "🔍 Inspect",
        "🔐 Enter Code",
        "🚪 Move"
    ])


    # -------- INSPECT --------

    with action_tab:

        object_name = st.text_input(
            "Bạn muốn kiểm tra thứ gì?",
            placeholder="Ví dụ: bàn, tủ, két..."
        )

        if st.button(
            "Inspect",
            use_container_width=True
        ):

            if object_name:

                result = inspect_object(
                    game,
                    object_name
                )

                st.session_state.game_log.append(
                    result["message"]
                )

                st.rerun()


    # -------- CODE --------

    with code_tab:

        code = st.text_input(
            "Nhập mã",
            max_chars=10
        )

        if st.button(
            "Submit Code",
            use_container_width=True
        ):

            if code:

                result = use_code(
                    game,
                    code
                )

                st.session_state.game_log.append(
                    result["message"]
                )

                st.rerun()


    # -------- MOVE --------

    with move_tab:

        destination = st.selectbox(
            "Đi đến:",
            [
                "library",
                "generator",
                "control"
            ]
        )

        if st.button(
            "Move",
            use_container_width=True
        ):

            result = move_room(
                game,
                destination
            )

            st.session_state.game_log.append(
                result["message"]
            )

            st.rerun()


# =========================
# RIGHT: GAME STATE
# =========================

with right:

    st.subheader("🎒 Inventory")

    if game.inventory:

        for item in game.inventory:
            st.success(
                f"• {item}"
            )

    else:
        st.caption(
            "Inventory trống."
        )


    st.divider()


    st.subheader("🧩 Clues")

    if game.discovered_clues:

        for clue in game.discovered_clues:
            st.info(
                clue
            )

    else:
        st.caption(
            "Chưa tìm thấy manh mối."
        )


    st.divider()


    st.subheader("✅ Solved")

    if game.solved_puzzles:

        for puzzle in game.solved_puzzles:
            st.write(
                f"✓ {puzzle}"
            )

    else:
        st.caption(
            "Chưa giải puzzle nào."
        )


    st.divider()


    # =========================
    # DEBUG STATE
    # =========================

    with st.expander(
        "🧠 Game State"
    ):

        st.json(
            game.get_summary()
        )


    # =========================
    # RESET
    # =========================

    if st.button(
        "🔄 Restart Game",
        use_container_width=True
    ):

        st.session_state.game = GameState()

        st.session_state.game_log = [
            "Bạn tỉnh dậy trong một phòng thí nghiệm tối om."
        ]

        st.rerun()