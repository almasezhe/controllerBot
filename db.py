#db.py
#инициализация бдшки
import sqlite3
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log"),
    ],
)

log = logging.getLogger("telegram-bot")


log.info("Connecting to SQLite database")
connection = sqlite3.connect("storage.db", check_same_thread=False)
cursor = connection.cursor()


log.info("Ensuring table Coords exists")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Coords (
    id INTEGER PRIMARY KEY,
    content TEXT,
    embeddings BLOB,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

log.info("Ensuring table TodoList exists")
cursor.execute("""
CREATE TABLE IF NOT EXISTS TodoList (
    id INTEGER PRIMARY KEY,
    task TEXT,
    description TEXT,
    deadline TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

log.info("Ensuring table Finances exists")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Finances (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    amount INT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    category TEXT,
    account TEXT
)
""")

log.info("Ensuring table FoodTracker exists")
cursor.execute("""
CREATE TABLE IF NOT EXISTS FoodTracker (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,              -- название еды
    calories INTEGER NOT NULL,       -- калории
    protein REAL DEFAULT 0,          -- белки
    fat REAL DEFAULT 0,              -- жиры
    carbs REAL DEFAULT 0,            -- углеводы
    weight REAL DEFAULT 0,           -- вес в граммах
    meal_type TEXT,                  -- breakfast / lunch / dinner / snack
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()