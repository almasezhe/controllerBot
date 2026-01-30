import sqlite3

log.info("Connecting to SQLite database")
connection = sqlite3.connect("storage.db", check_same_thread=False)
cursor = connection.cursor()


log.info("Ensuring table Coords exists")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Coords (
    content TEXT,
    embeddings BLOB,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

log.info("Ensuring table TodoList exists")
cursor.execute("""
CREATE TABLE IF NOT EXISTS TodoList (
    task TEXT,
    description TEXT,
    deadline TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()