import csv
import requests

BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# TEST CASES
# ============================================================

TEST_CASES = [
    {
        "name": "safe_code",
        "save_message": "Tôi phát hiện manh mối: mã két sắt là 4132.",
        "object": "computer",
        "question": "Mã két sắt mà tôi phát hiện trước đó là gì?",
        "expected": "4132",
    },
    {
        "name": "door_code",
        "save_message": "Tôi phát hiện manh mối: mã cửa phòng điều khiển là 7291.",
        "object": "terminal",
        "question": "Mã cửa phòng điều khiển là gì?",
        "expected": "7291",
    },
    {
        "name": "locker_code",
        "save_message": "Tôi phát hiện manh mối: mã tủ chứa vật phẩm là 5580.",
        "object": "note",
        "question": "Mã tủ chứa vật phẩm là gì?",
        "expected": "5580",
    },
    {
        "name": "reactor_code",
        "save_message": "Tôi phát hiện manh mối: mã kích hoạt lò phản ứng là 2468.",
        "object": "screen",
        "question": "Mã kích hoạt lò phản ứng là gì?",
        "expected": "2468",
    },
    {
        "name": "exit_code",
        "save_message": "Tôi phát hiện manh mối: mã thoát hiểm cuối cùng là 9007.",
        "object": "poster",
        "question": "Mã thoát hiểm cuối cùng là gì?",
        "expected": "9007",
    }
]


NOISE_EVENTS = [
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


# ============================================================
# API HELPERS
# ============================================================

def interact(action, obj, message):
    payload = {
        "action": action,
        "object": obj,
        "room": "laboratory",
        "message": message
    }

    response = requests.post(
        f"{BASE_URL}/interact",
        json=payload
    )

    response.raise_for_status()

    return response.json()


def reset_game():
    response = requests.post(
        f"{BASE_URL}/reset"
    )

    response.raise_for_status()


# ============================================================
# NO MEMORY
# ============================================================

def evaluate_no_memory(case):

    # Không có lịch sử
    recalled = 0

    return {
        "method": "No Memory",
        "case": case["name"],
        "recall": recalled,
        "stored_memories": 0,
        "retrieved_memories": 0,
        "irrelevant_retrievals": 0,
        "avg_distance": 0
    }


# ============================================================
# SLIDING WINDOW
# ============================================================

def evaluate_sliding_window(case):

    history = []

    history.append(
        case["save_message"]
    )

    for _, message in NOISE_EVENTS:
        history.append(message)

    # sliding window = 4 messages
    window = history[-4:]

    recalled = (
        1
        if any(
            case["expected"] in text
            for text in window
        )
        else 0
    )

    return {
        "method": "Sliding Window",
        "case": case["name"],
        "recall": recalled,
        "stored_memories": 0,
        "retrieved_memories": len(window),
        "irrelevant_retrievals": len(window),
        "avg_distance": 0
    }


# ============================================================
# SELECTIVE LONG-TERM MEMORY
# ============================================================

def evaluate_selective_ltm(case):

    reset_game()

    # --------------------------
    # SAVE IMPORTANT MEMORY
    # --------------------------

    save_result = interact(
        "inspect",
        case["object"],
        case["save_message"]
    )

    stored_memories = (
        1
        if save_result["memory_saved"]
        is not None
        else 0
    )


    # --------------------------
    # 20 NOISE EVENTS
    # --------------------------

    for obj, message in NOISE_EVENTS:

        interact(
            "inspect",
            obj,
            message
        )


    # --------------------------
    # ASK AGAIN
    # --------------------------

    recall_result = interact(
        "ask",
        "safe",
        case["question"]
    )

    dialogue = recall_result[
        "dialogue"
    ]

    memories = recall_result[
        "memory_used"
    ]


    recalled = (
        1
        if case["expected"] in dialogue
        else 0
    )


    # --------------------------
    # IRRELEVANT RETRIEVAL
    # --------------------------

    irrelevant = 0

    distances = []

    for memory in memories:

        text = memory["text"]

        if case["expected"] not in text:
            irrelevant += 1

        distances.append(
            memory["distance"]
        )


    if distances:

        avg_distance = (
            sum(distances)
            / len(distances)
        )

    else:

        avg_distance = 0


    return {
        "method":
            "Selective Long-Term Memory",

        "case":
            case["name"],

        "recall":
            recalled,

        "stored_memories":
            stored_memories,

        "retrieved_memories":
            len(memories),

        "irrelevant_retrievals":
            irrelevant,

        "avg_distance":
            round(
                avg_distance,
                4
            )
    }


# ============================================================
# RUN BENCHMARK
# ============================================================

all_results = []


for case in TEST_CASES:

    print(
        f"\nTesting case: "
        f"{case['name']}"
    )

    result_no_memory = (
        evaluate_no_memory(case)
    )

    result_window = (
        evaluate_sliding_window(case)
    )

    result_ltm = (
        evaluate_selective_ltm(case)
    )

    all_results.extend([
        result_no_memory,
        result_window,
        result_ltm
    ])


# ============================================================
# SUMMARY
# ============================================================

methods = [
    "No Memory",
    "Sliding Window",
    "Selective Long-Term Memory"
]


summary = []


for method in methods:

    method_results = [
        result
        for result in all_results
        if result["method"] == method
    ]

    total_tests = len(
        method_results
    )

    recall_count = sum(
        result["recall"]
        for result
        in method_results
    )

    recall_accuracy = (
        recall_count
        / total_tests
        * 100
    )

    total_stored = sum(
        result["stored_memories"]
        for result
        in method_results
    )

    total_retrieved = sum(
        result["retrieved_memories"]
        for result
        in method_results
    )

    irrelevant = sum(
        result["irrelevant_retrievals"]
        for result
        in method_results
    )

    if total_retrieved > 0:

        irrelevant_rate = (
            irrelevant
            / total_retrieved
            * 100
        )

    else:

        irrelevant_rate = 0


    summary.append({
        "method": method,
        "tests": total_tests,
        "recall_accuracy": round(
            recall_accuracy,
            2
        ),
        "stored_memories": total_stored,
        "retrieved_memories":
            total_retrieved,
        "irrelevant_rate":
            round(
                irrelevant_rate,
                2
            )
    })


# ============================================================
# PRINT RESULT
# ============================================================

print("\n")
print("=" * 105)

print(
    "PROJECT ECHO - MEMORY BENCHMARK"
)

print("=" * 105)

print(
    f"{'Method':32}"
    f"{'Recall Accuracy':18}"
    f"{'Stored':12}"
    f"{'Retrieved':14}"
    f"{'Irrelevant':15}"
)

print("-" * 105)


for row in summary:

    print(
        f"{row['method']:32}"
        f"{str(row['recall_accuracy']) + '%':18}"
        f"{row['stored_memories']:<12}"
        f"{row['retrieved_memories']:<14}"
        f"{str(row['irrelevant_rate']) + '%':15}"
    )


print("=" * 105)


# ============================================================
# EXPORT DETAILED CSV
# ============================================================

with open(
    "benchmark_results.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "method",
            "case",
            "recall",
            "stored_memories",
            "retrieved_memories",
            "irrelevant_retrievals",
            "avg_distance"
        ]
    )

    writer.writeheader()

    writer.writerows(
        all_results
    )


# ============================================================
# EXPORT SUMMARY CSV
# ============================================================

with open(
    "benchmark_summary.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "method",
            "tests",
            "recall_accuracy",
            "stored_memories",
            "retrieved_memories",
            "irrelevant_rate"
        ]
    )

    writer.writeheader()

    writer.writerows(
        summary
    )


print(
    "\n✅ Exported:"
)

print(
    " - benchmark_results.csv"
)

print(
    " - benchmark_summary.csv"
)