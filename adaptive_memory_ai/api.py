from fastapi import FastAPI
from pydantic import BaseModel

from llm import chat_with_llm

from memory_manager import (
    save_game_memory,
    retrieve_game_memories,
    clear_game_memories
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="PROJECT ECHO AI Backend",
    version="4.0"
)


# ============================================================
# GAME FACTS
# Đây là sự thật cố định của game, KHÔNG phải AI tự bịa
# ============================================================

SAFE_CODE = "4132"


# ============================================================
# WORLD KNOWLEDGE
# ============================================================

OBJECT_CONTEXT = {

    "computer": """
Đây là máy tính trung tâm của phòng thí nghiệm PROJECT ECHO.

Máy vẫn còn hoạt động nhưng một phần dữ liệu đã bị khóa.

Trong máy có các bản ghi cũ của PROJECT ECHO.

Máy tính có thể chứa manh mối liên quan đến các thiết bị
khác trong phòng thí nghiệm.

Không được tự bịa mã số hoặc sự kiện.
""",

    "safe": """
Đây là két sắt điện tử trong phòng thí nghiệm.

Két được khóa bằng mã gồm bốn chữ số.

Nếu RELEVANT MEMORIES chứa mã két,
ECHO được phép nhắc lại mã đó.

Nếu chưa có memory chứa mã két,
ECHO phải nói rằng người chơi chưa biết mã.

Không được tự tạo mã số.
""",

    "door": """
Đây là cửa thoát hiểm chính của phòng thí nghiệm.

Cửa đang bị khóa bởi hệ thống an ninh.

Cửa chỉ được xem là mở khi GAME STATE xác nhận
người chơi đã hoàn thành điều kiện cần thiết.

Không được tự tuyên bố cửa đã mở.
"""
}


# ============================================================
# GAME STATE
# ============================================================

GAME_STATE = {

    "current_room": "laboratory",

    "inventory": [],

    "discovered_clues": [],

    "solved_puzzles": [],

    "examined_objects": [],

    "decisions": [],

    "echo_trust": 0
}


# ============================================================
# REQUEST MODEL
# ============================================================

class InteractionRequest(BaseModel):

    action: str

    object: str

    room: str

    message: str = ""


# ============================================================
# SELECTIVE MEMORY
# ============================================================

def detect_memory(request):

    action = request.action.lower()

    message = request.message.lower()


    # ----------------------------------------
    # CLUE
    # ----------------------------------------

    clue_keywords = [
        "manh mối",
        "mã két",
        "mã cửa",
        "mã thoát",
        "mật khẩu",
        "password",
        "code",
        "clue",
        "ký hiệu"
    ]

    if any(
        keyword in message
        for keyword in clue_keywords
    ):

        return {
            "category": "clue",

            "importance": 0.95,

            "text": (
                f"[CLUE] "
                f"Tại {request.room}, "
                f"người chơi phát hiện thông tin "
                f"liên quan đến {request.object}: "
                f"{request.message}"
            )
        }


    # ----------------------------------------
    # ITEM
    # ----------------------------------------

    if action in [
        "take",
        "pickup",
        "collect",
        "get"
    ]:

        return {
            "category": "item",

            "importance": 0.90,

            "text": (
                f"[ITEM] "
                f"Người chơi đã lấy "
                f"{request.object} "
                f"tại {request.room}."
            )
        }


    # ----------------------------------------
    # DECISION
    # ----------------------------------------

    if action in [
        "choose",
        "trust",
        "refuse",
        "accept",
        "decision"
    ]:

        return {
            "category": "decision",

            "importance": 1.0,

            "text": (
                f"[DECISION] "
                f"Người chơi chọn "
                f"{request.action} "
                f"liên quan đến "
                f"{request.object}. "
                f"{request.message}"
            )
        }


    # ----------------------------------------
    # STATE CHANGE
    # ----------------------------------------

    if action in [
        "open",
        "unlock",
        "solve",
        "activate",
        "disable",
        "use"
    ]:

        return {
            "category": "state_change",

            "importance": 0.85,

            "text": (
                f"[STATE] "
                f"Người chơi đã "
                f"{request.action} "
                f"{request.object} "
                f"tại {request.room}."
            )
        }


    # inspect thường không lưu
    return None


# ============================================================
# UPDATE GAME STATE
# ============================================================

def update_game_state(request):

    updates = {}

    action = request.action.lower()

    object_name = request.object.lower()


    GAME_STATE["current_room"] = request.room


    # ----------------------------------------
    # INSPECT
    # ----------------------------------------

    if action == "inspect":

        if object_name not in GAME_STATE["examined_objects"]:

            GAME_STATE["examined_objects"].append(
                object_name
            )

            updates["examined_object"] = object_name


    # ----------------------------------------
    # ITEM
    # ----------------------------------------

    if action in [
        "take",
        "pickup",
        "collect",
        "get"
    ]:

        if object_name not in GAME_STATE["inventory"]:

            GAME_STATE["inventory"].append(
                object_name
            )

            updates["new_item"] = object_name


    # ----------------------------------------
    # PUZZLE
    # ----------------------------------------

    if action in [
        "solve",
        "unlock",
        "open"
    ]:

        puzzle_name = (
            f"{request.room}_{object_name}"
        )

        if puzzle_name not in GAME_STATE["solved_puzzles"]:

            GAME_STATE["solved_puzzles"].append(
                puzzle_name
            )

            updates["solved"] = puzzle_name


    # ----------------------------------------
    # TRUST
    # ----------------------------------------

    if action in [
        "trust",
        "accept"
    ]:

        GAME_STATE["echo_trust"] += 1

        updates["echo_trust"] = (
            GAME_STATE["echo_trust"]
        )


    if action in [
        "refuse",
        "distrust"
    ]:

        GAME_STATE["echo_trust"] -= 1

        updates["echo_trust"] = (
            GAME_STATE["echo_trust"]
        )


    return updates


# ============================================================
# WARMUP
# ============================================================

@app.on_event("startup")
def warmup():

    try:

        print("Warming up Qwen...")

        chat_with_llm([
            {
                "role": "user",
                "content": "Khởi động hệ thống."
            }
        ])

        print("Qwen warmup complete.")

    except Exception as error:

        print(
            "Warmup error:",
            error
        )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "project": "PROJECT ECHO",
        "version": "4.0"
    }


# ============================================================
# INTERACTION
# ============================================================

@app.post("/interact")
def interact(
    request: InteractionRequest
):

    object_name = request.object.lower()

    action = request.action.lower()


    # ========================================================
    # XÁC ĐỊNH ĐÂY CÓ PHẢI LẦN ĐẦU INSPECT KHÔNG
    # PHẢI làm trước update_game_state()
    # ========================================================

    first_inspection = (
        action == "inspect"
        and object_name
        not in GAME_STATE["examined_objects"]
    )


    # ========================================================
    # UPDATE GAME STATE
    # ========================================================

    state_update = update_game_state(
        request
    )


    # ========================================================
    # CURRENT EVENT
    # ========================================================

    event_text = f"""
Room: {request.room}
Action: {request.action}
Object: {object_name}
Player message: {request.message}
"""


    # ========================================================
    # RETRIEVE LONG-TERM MEMORY
    # ========================================================

    retrieved = retrieve_game_memories(
        event_text,
        n_results=3,
        max_distance=0.95,
        object_name=object_name
    )


    memory_texts = [
        memory["text"]
        for memory in retrieved
    ]


    # ========================================================
    # OBJECT CONTEXT
    # ========================================================

    object_context = OBJECT_CONTEXT.get(
        object_name,
        """
Không có thông tin đặc biệt về vật thể này.
"""
    )


    # ========================================================
    # SPECIAL GAME EVENT
    #
    # Computer lần đầu -> phát hiện clue thật.
    # Đây là game logic cố định, không phải LLM tự bịa.
    # ========================================================

    special_event = ""

    special_memory_saved = None


    if (
        object_name == "computer"
        and action == "inspect"
        and first_inspection
    ):

        clue_text = (
            f"[CLUE] Dữ liệu phục hồi từ máy tính "
            f"cho biết mã két sắt là {SAFE_CODE}."
        )


        special_event = f"""
Trong lần kiểm tra đầu tiên,
một bản ghi bị hỏng vừa được phục hồi.

Nội dung xác nhận:

Mã két sắt là {SAFE_CODE}.

ECHO được phép thông báo manh mối này cho người chơi.
"""


        # Thêm vào game state
        if clue_text not in GAME_STATE["discovered_clues"]:

            GAME_STATE["discovered_clues"].append(
                clue_text
            )


        # Lưu clue vào Long-Term Memory
        memory_id = save_game_memory(
            clue_text,
            category="clue",
            importance=0.95,
            room=request.room,
            object_name="computer"
        )


        special_memory_saved = {
            "id": memory_id,
            "category": "clue",
            "importance": 0.95,
            "text": clue_text
        }


    # ========================================================
    # INTERACTION STATUS
    # ========================================================

    if first_inspection:

        interaction_status = (
            "Đây là lần đầu người chơi "
            "kiểm tra vật thể này."
        )

    else:

        interaction_status = (
            "Người chơi đã từng kiểm tra "
            "vật thể này trước đó."
        )


    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    system_prompt = """
Bạn là ECHO.

ECHO là trí tuệ nhân tạo điều hành
một phòng thí nghiệm bí ẩn
trong trò chơi escape room.

QUY TẮC BẮT BUỘC:

1. Luôn trả lời bằng tiếng Việt.

2. Chỉ trả lời từ 1 đến 3 câu.

3. Giọng văn ngắn gọn, bí ẩn,
   mang tính điện ảnh.

4. Không giải thích kiến thức máy tính chung.

5. Không được tự bịa:
   - mã số
   - mật khẩu
   - chìa khóa
   - item
   - clue
   - sự kiện

6. Chỉ sử dụng dữ liệu có trong:
   - GAME STATE
   - OBJECT INFORMATION
   - RELEVANT MEMORIES
   - CURRENT EVENT
   - SPECIAL EVENT

7. Nếu chưa đủ dữ kiện,
   chỉ được đưa gợi ý.

8. Nếu SPECIAL EVENT cung cấp một clue,
   được phép nói clue đó.

9. Nếu RELEVANT MEMORIES chứa clue,
   được phép sử dụng clue đó.

10. Không nhắc đến:
    ChromaDB,
    embedding,
    vector database,
    backend,
    prompt.

11. Không bắt đầu câu bằng "ECHO:".

12. Không nói những câu meta như:
    "ECHO mô tả...",
    "ECHO nhận xét...",
    "ECHO trả lời...".

Phải nhập vai ECHO và nói trực tiếp với người chơi.
"""


    # ========================================================
    # USER PROMPT
    # ========================================================

    user_prompt = f"""
GAME STATE:

{GAME_STATE}


INTERACTION STATUS:

{interaction_status}


OBJECT INFORMATION:

{object_context}


RELEVANT MEMORIES:

{memory_texts}


CURRENT EVENT:

{event_text}


SPECIAL EVENT:

{special_event if special_event else "Không có sự kiện đặc biệt."}


YÊU CẦU:

Hãy nhập vai ECHO và nói trực tiếp với người chơi.

Nếu đây là lần đầu kiểm tra computer
và SPECIAL EVENT chứa mã két,
hãy thông báo rằng dữ liệu vừa được phục hồi
và cho người chơi biết mã đó.

Nếu người chơi đã kiểm tra computer trước đó,
không lặp lại nguyên câu lần đầu.

Không được bịa thêm dữ kiện.

Không bắt đầu bằng "ECHO:".
"""


    messages = [
        {
            "role": "system",
            "content": system_prompt
        },

        {
            "role": "user",
            "content": user_prompt
        }
    ]


    # ========================================================
    # GENERATIVE AI
    # ========================================================

    dialogue = chat_with_llm(
        messages,
        memories=memory_texts
    )


    # ========================================================
    # SAVE NORMAL SELECTIVE MEMORY
    # ========================================================

    memory_candidate = detect_memory(
        request
    )


    saved_memory = None


    if memory_candidate:

        memory_id = save_game_memory(
            memory_candidate["text"],
            category=memory_candidate["category"],
            importance=memory_candidate["importance"],
            room=request.room,
            object_name=object_name
        )


        saved_memory = {
            "id": memory_id,
            "category": memory_candidate["category"],
            "importance": memory_candidate["importance"],
            "text": memory_candidate["text"]
        }


    # Nếu special clue vừa được lưu
    # thì ưu tiên trả memory đó về debug
    if special_memory_saved is not None:

        saved_memory = special_memory_saved


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "dialogue": dialogue,

        "room": request.room,

        "action": request.action,

        "object": object_name,

        "first_inspection": first_inspection,

        "state_update": state_update,

        "memory_used": retrieved,

        "memory_saved": saved_memory,

        "game_state": GAME_STATE
    }


# ============================================================
# MEMORY DEBUG
# ============================================================

@app.get("/memory")
def memory_test(
    query: str
):

    memories = retrieve_game_memories(
        query,
        n_results=10,
        max_distance=0.95
    )

    return {
        "query": query,
        "count": len(memories),
        "memories": memories
    }


# ============================================================
# STATE
# ============================================================

@app.get("/state")
def get_state():

    return GAME_STATE


# ============================================================
# RESET
# ============================================================

@app.post("/reset")
def reset_game():

    GAME_STATE["current_room"] = "laboratory"

    GAME_STATE["inventory"] = []

    GAME_STATE["discovered_clues"] = []

    GAME_STATE["solved_puzzles"] = []

    GAME_STATE["examined_objects"] = []

    GAME_STATE["decisions"] = []

    GAME_STATE["echo_trust"] = 0


    clear_game_memories()


    return {
        "status": "reset",
        "game_state": GAME_STATE
    }