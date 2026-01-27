import logging
import os
import sqlite3
import pickle

import whisper
import numpy as np
import faiss

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ───────────────────────── LOGGING ─────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log"),
    ],
)

log = logging.getLogger("telegram-bot")

# ───────────────────────── ENV ─────────────────────────

log.info("Loading environment variables")
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    log.critical("BOT_TOKEN not found in environment")
    raise RuntimeError("BOT_TOKEN missing")

# ───────────────────────── MODELS ─────────────────────────

log.info("Loading sentence transformer model")
model = SentenceTransformer("all-MiniLM-L6-v2")

audio_model_name = "base"
log.info("Loading Whisper model: %s", audio_model_name)
audio_model = whisper.load_model(audio_model_name)

# ───────────────────────── DATABASE ─────────────────────────

log.info("Connecting to SQLite database")
connection = sqlite3.connect("vectors.db", check_same_thread=False)
cursor = connection.cursor()

log.info("Ensuring table exists")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Coords (
    content TEXT,
    embeddings BLOB,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
connection.commit()

# ───────────────────────── HANDLERS ─────────────────────────

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    log.info("Hello command from user_id=%s", user.id)
    await update.message.reply_text(f"Hello {user.first_name}")


async def transcript_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    log.info("Voice message received from user_id=%s", user.id)

    try:
        new_file = await update.message.effective_attachment.get_file()
        await update.message.reply_text("In progress...")

        log.info("Downloading voice file")
        await new_file.download_to_drive("voice.oga")

        log.info("Starting Whisper transcription")
        result = audio_model.transcribe("voice.oga")

        text = result.get("text", "")
        segments = "\n".join(
            f'{s["start"]:.2f}–{s["end"]:.2f}: {s["text"]}'
            for s in result.get("segments", [])
        )

        log.info(
            "Transcription finished, chars=%d, segments=%d",
            len(text),
            len(result.get("segments", [])),
        )

        await update.message.reply_text(text + "\n\n" + segments)

    except Exception:
        log.exception("Voice transcription failed")
        await update.message.reply_text("Ошибка при распознавании аудио")

    finally:
        if os.path.exists("voice.oga"):
            os.remove("voice.oga")
            log.debug("Temporary voice file removed")


async def note_embedding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    sentence = update.message.text or ""

    log.info("Note command from user_id=%s", user.id)

    text = sentence.removeprefix("/note ").lstrip()
    if not text:
        log.warning("Empty note received")
        await update.message.reply_text("Пустая заметка")
        return

    try:
        log.info("Encoding note, chars=%d", len(text))
        embeddings = model.encode(text)

        embeddings_blob = pickle.dumps(embeddings)

        log.info("Saving note to database")
        cursor.execute(
            "INSERT INTO Coords (content, embeddings) VALUES (?, ?)",
            (text, embeddings_blob),
        )
        connection.commit()

        await update.message.reply_text("Готово!")

    except Exception:
        log.exception("Failed to save note")
        await update.message.reply_text("Ошибка при сохранении заметки")


def find_similar(query: str, index, texts, k=5):
    log.debug("Encoding search query")
    q = model.encode(query, convert_to_numpy=True).astype("float32")
    q = q.reshape(1, -1)
    faiss.normalize_L2(q)

    log.debug("Running FAISS search, k=%d", k)
    scores, ids = index.search(q, k)

    return [(texts[i], scores[0][j]) for j, i in enumerate(ids[0])]


async def faiss_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    sentence = update.message.text or ""

    log.info("Search command from user_id=%s", user.id)

    text = sentence.removeprefix("/search ").lstrip()
    if not text:
        log.warning("Empty search query")
        await update.message.reply_text("Пустой запрос")
        return

    try:
        log.info("Loading embeddings from database")
        cursor.execute("SELECT * FROM Coords")
        coords = cursor.fetchall()

        if not coords:
            log.warning("Database is empty")
            await update.message.reply_text("База пуста")
            return

        texts = []
        embeddings_list = []

        for content, blob, _ in coords:
            texts.append(content)
            embeddings_list.append(pickle.loads(blob))

        log.info("Building FAISS index, vectors=%d", len(embeddings_list))
        embeddings = np.vstack(embeddings_list).astype("float32")
        faiss.normalize_L2(embeddings)

        d = embeddings.shape[1]
        index = faiss.IndexFlatIP(d)
        index.add(embeddings)

        log.info("Running similarity search")
        results = find_similar(text, index, texts, k=2)

        msg = "\n\n".join(
            f"📌 {t}\n🔎 similarity: {float(score):.4f}"
            for t, score in results
        )

        await update.message.reply_text(msg)

    except Exception:
        log.exception("Search failed")
        await update.message.reply_text("Ошибка поиска")

# ───────────────────────── MAIN ─────────────────────────

if __name__ == "__main__":
    log.info("Starting Telegram application")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("note", note_embedding))
    app.add_handler(CommandHandler("search", faiss_search))
    app.add_handler(MessageHandler(filters.VOICE, transcript_voice))

    log.info("Bot is running")
    app.run_polling()
