import requests
import time

BASE_URL = "http://127.0.0.1:8000"


def interact(action, object_name, room, message):
    payload = {
        "action": action,
        "object": object_name,
        "room": room,
        "message": message
    }

    response = requests.post(
        f"{BASE_URL}/interact",
        json=payload
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# 1. RESET GAME
# ==========================================

print("\n===== RESET GAME =====")

response = requests.post(
    f"{BASE_URL}/reset"
)

print(response.json())


# ==========================================
# 2. SAVE IMPORTANT CLUE
# ==========================================

print("\n===== SAVE IMPORTANT CLUE =====")

result = interact(
    action="inspect",
    object_name="computer",
    room="laboratory",
    message="Tôi phát hiện manh mối: mã két sắt là 4132."
)

print("Dialogue:")
print(result["dialogue"])

print("\nMemory saved:")
print(result["memory_saved"])


# ==========================================
# 3. ADD NOISE EVENTS
# ==========================================

noise_events = [
    ("table", "Tôi kiểm tra chiếc bàn."),
    ("wall", "Tôi nhìn kỹ bức tường."),
    ("lamp", "Tôi kiểm tra chiếc đèn."),
    ("chair", "Tôi kiểm tra chiếc ghế."),
    ("window", "Tôi nhìn qua cửa sổ."),
    ("floor", "Tôi kiểm tra mặt sàn."),
    ("cabinet", "Tôi nhìn chiếc tủ."),
    ("pipe", "Tôi kiểm tra đường ống."),
    ("door", "Tôi kiểm tra cánh cửa."),
    ("camera", "Tôi nhìn camera an ninh."),
    ("desk", "Tôi kiểm tra bàn làm việc."),
    ("screen", "Tôi nhìn màn hình cũ."),
    ("box", "Tôi kiểm tra chiếc hộp."),
    ("book", "Tôi xem quyển sách."),
    ("clock", "Tôi nhìn chiếc đồng hồ."),
    ("vent", "Tôi kiểm tra khe thông gió."),
    ("ceiling", "Tôi nhìn lên trần nhà."),
    ("poster", "Tôi nhìn tấm áp phích."),
    ("switch", "Tôi kiểm tra công tắc."),
    ("shelf", "Tôi nhìn chiếc kệ.")
]


print("\n===== ADDING 20 NOISE EVENTS =====")

for i, (obj, message) in enumerate(
    noise_events,
    start=1
):

    interact(
        action="inspect",
        object_name=obj,
        room="laboratory",
        message=message
    )

    print(
        f"Noise {i:02d}/20: {obj}"
    )


# ==========================================
# 4. TEST LONG-TERM RECALL
# ==========================================

print("\n===== LONG-TERM RECALL TEST =====")

result = interact(
    action="ask",
    object_name="safe",
    room="laboratory",
    message="ECHO, mã két sắt mà tôi đã phát hiện trước đó là gì?"
)


print("\nECHO:")
print(result["dialogue"])


print("\nMEMORY USED:")

for memory in result["memory_used"]:

    print(
        "-",
        memory["text"]
    )

    print(
        "  category:",
        memory["category"]
    )

    print(
        "  importance:",
        memory["importance"]
    )

    print(
        "  distance:",
        memory["distance"]
    )


# ==========================================
# 5. SIMPLE RESULT
# ==========================================

dialogue = result["dialogue"]

memory_text = " ".join(
    memory["text"]
    for memory
    in result["memory_used"]
)


if (
    "4132" in dialogue
    or "4132" in memory_text
):

    print(
        "\n✅ TEST PASSED:"
        " Long-term memory recalled 4132."
    )

else:

    print(
        "\n❌ TEST FAILED:"
        " Memory did not recall 4132."
    )