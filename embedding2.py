from sentence_transformers import SentenceTransformer
import sqlite3
import pickle
import numpy as np
import faiss
# 1. Load a pretrained Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")
connection = sqlite3.connect('vectors.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Coords (
content TEXT,
embeddings BLOB,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

# embeddings
#embeddings1 = model.encode("Nazarbayev Gay")

#TODO
# Retrieve data from SQL and search from them
# Add FAISS searchff
cursor.execute('SELECT * FROM Coords')
coords = cursor.fetchall()
texts = []
embeddings_list = []
dates=[]

for content, blob, date in coords:
    texts.append(content)
    embeddings_list.append(pickle.loads(blob))
    dates.append(date)

embeddings = np.vstack(embeddings_list).astype("float32")
print(embeddings.shape) 


faiss.normalize_L2(embeddings)
d = embeddings.shape[1]
index = faiss.IndexFlatIP(d)
index.add(embeddings)

def find_similar(query, k=5):
    q = model.encode(query, convert_to_numpy=True).astype("float32")
    q = q.reshape(1, -1)
    faiss.normalize_L2(q)

    scores, ids = index.search(q, k)
    return [(texts[i], scores[0][j]) for j, i in enumerate(ids[0])]

print(find_similar("Nazarbayev", 2))

connection.commit()
connection.close()
