import uuid
import chromadb
from sentence_transformers import SentenceTransformer


# ==============================
# EMBEDDING MODEL
# ==============================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def get_embedding(text):
    return embedding_model.encode(text).tolist()


# ==============================
# CHROMADB
# ==============================

client = chromadb.PersistentClient(
    path="./database"
)


# Memory chatbot cũ
collection = client.get_or_create_collection(
    name="long_term_memory"
)


# Memory riêng PROJECT ECHO
game_collection = client.get_or_create_collection(
    name="project_echo_memory"
)


# ============================================================
# CHATBOT MEMORY CŨ
# ============================================================

def save_memory(
    text,
    category="general",
    importance=1.0
):
    memory_id = str(uuid.uuid4())

    collection.add(
        ids=[memory_id],
        documents=[text],
        embeddings=[get_embedding(text)],
        metadatas=[{
            "category": category,
            "importance": importance
        }]
    )

    return memory_id


def retrieve_memories(
    query,
    n_results=3
):
    count = collection.count()

    if count == 0:
        return []

    n_results = min(
        n_results,
        count
    )

    results = collection.query(
        query_embeddings=[
            get_embedding(query)
        ],
        n_results=n_results
    )

    if not results["documents"]:
        return []

    return results["documents"][0]


# ============================================================
# PROJECT ECHO MEMORY
# ============================================================

def save_game_memory(
    text,
    category="game_event",
    importance=0.5,
    room="unknown",
    object_name="unknown"
):
    memory_id = str(uuid.uuid4())

    game_collection.add(
        ids=[memory_id],
        documents=[text],
        embeddings=[
            get_embedding(text)
        ],
        metadatas=[{
            "category": category,
            "importance": float(importance),
            "room": room,
            "object": object_name
        }]
    )

    return memory_id
def retrieve_game_memories(
    query,
    n_results=3,
    max_distance=0.95,
    object_name=None
):
    count = game_collection.count()

    if count == 0:
        return []

    search_results = min(
        max(n_results * 3, n_results),
        count
    )

    results = game_collection.query(
        query_embeddings=[
            get_embedding(query)
        ],
        n_results=search_results,
        include=[
            "documents",
            "distances",
            "metadatas"
        ]
    )

    if not results["documents"]:
        return []

    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    memories = []

    for document, distance, metadata in zip(
        documents,
        distances,
        metadatas
    ):
        distance = float(distance)

        # Memory quá xa về ngữ nghĩa thì bỏ
        if distance > max_distance:
            continue

        category = metadata.get(
            "category",
            "game_event"
        )

        memory_object = metadata.get(
            "object",
            ""
        )

        # Nếu đang tương tác object cụ thể:
        # - ưu tiên memory cùng object
        # - clue vẫn được phép dùng chéo object
        if object_name is not None:
            if (
                memory_object != object_name
                and category != "clue"
            ):
                continue

        memories.append({
            "text": document,
            "distance": round(
                distance,
                4
            ),
            "category": category,
            "importance": metadata.get(
                "importance",
                0.5
            ),
            "room": metadata.get(
                "room",
                "unknown"
            ),
            "object": memory_object
        })

    # Importance cao trước,
    # nếu bằng nhau thì distance thấp trước
    memories.sort(
        key=lambda x: (
            -float(x["importance"]),
            float(x["distance"])
        )
    )

    return memories[:n_results]


def clear_game_memories():
    global game_collection

    try:
        client.delete_collection(
            "project_echo_memory"
        )
    except Exception:
        pass

    game_collection = client.get_or_create_collection(
        name="project_echo_memory"
    )