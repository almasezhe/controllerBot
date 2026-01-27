from sentence_transformers import SentenceTransformer
import sqlite3
import pickle
import numpy as np
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

sentences = "loh UNIVER"

# embeddings
embeddings = model.encode(sentences)
embeddings_blob = pickle.dumps(embeddings)

print(embeddings.shape)
cursor.execute(
    "INSERT INTO Coords (content, embeddings) VALUES (?, ?)",
    (sentences, embeddings_blob)
)

embeddings1 = model.encode("Nazarbayev Gay")

#TODO
# Retrieve data from SQL and search from them
# Add FAISS search

#cursor.execute('SELECT * FROM Users')
#users = cursor.fetchall()

similarities = model.similarity(embeddings, embeddings1)
print(similarities)

connection.commit()
connection.close()
