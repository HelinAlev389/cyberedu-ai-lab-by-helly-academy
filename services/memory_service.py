import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

from extensions import db
from models.ai_memory import AIMemory

client = OpenAI()


def get_embedding(text: str, model="text-embedding-3-small"):
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding


def save_memory(user_id, session_id, text, tags=None):
    emb = get_embedding(text)
    mem = AIMemory(
        user_id=user_id,
        session_id=session_id,
        text=text,
        embedding=emb,
        tags=tags or []
    )
    db.session.add(mem)
    db.session.commit()


def search_memory(user_id, query_text, top_k=3):
    query_vec = np.array(get_embedding(query_text)).reshape(1, -1)
    all_mem = AIMemory.query.filter_by(user_id=user_id).all()

    scored = []
    for mem in all_mem:
        vec = np.array(mem.embedding).reshape(1, -1)
        sim = cosine_similarity(query_vec, vec)[0][0]
        scored.append((mem.text, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [txt for txt, _ in scored[:top_k]]
