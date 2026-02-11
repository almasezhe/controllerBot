#main.py 
# основная логика бота
import os
#import pickle

#import whisper
#import numpy as np
#import faiss

from dotenv import load_dotenv
#from sentence_transformers import SentenceTransformer

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from db import log
#from note_taking import note_embedding, faiss_search
from tracker import add_record, delete, last, total
#import todo
#TODO todo 


# ───────────────────────── ENV ─────────────────────────

log.info("Loading environment variables")
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    log.critical("BOT_TOKEN not found in environment")
    raise RuntimeError("BOT_TOKEN missing")

# ───────────────────────── MODELS ─────────────────────────

#log.info("Loading sentence transformer model")
#model = SentenceTransformer("all-MiniLM-L6-v2")

#audio_model_name = "base"
#log.info("Loading Whisper model: %s", audio_model_name)
#audio_model = whisper.load_model(audio_model_name)



# ───────────────────────── HANDLERS ─────────────────────────

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    log.info("Hello command from user_id=%s", user.id)
    await update.message.reply_text(f"Hello {user.first_name}")


#async def transcript_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#    user = update.effective_user
#    log.info("Voice message received from user_id=%s", user.id)
#
#    try:
#        new_file = await update.message.effective_attachment.get_file()
#        await update.message.reply_text("In progress...")
#
#        log.info("Downloading voice file")
#        await new_file.download_to_drive("voice.oga")
#
#        log.info("Starting Whisper transcription")
#        result = audio_model.transcribe("voice.oga")
#
#        text = result.get("text", "")
#        segments = "\n".join(
#            f'{s["start"]:.2f}–{s["end"]:.2f}: {s["text"]}'
#            for s in result.get("segments", [])
#        )
#
#        log.info(
#            "Transcription finished, chars=%d, segments=%d",
#            len(text),
#            len(result.get("segments", [])),
#        )
#
#        await update.message.reply_text(text + "\n\n" + segments)
#
#    except Exception:
#        log.exception("Voice transcription failed")
#        await update.message.reply_text("Ошибка при распознавании аудио")
#
#    finally:
#        if os.path.exists("voice.oga"):
#            os.remove("voice.oga")
#            log.debug("Temporary voice file removed")
#
#
async def error_handler(update, context):
    log.error("Ошибка: %s", context.error)


# ───────────────────────── MAIN ─────────────────────────

if __name__ == "__main__":
    log.info("Starting Telegram application")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("hello", hello))
    #app.add_handler(CommandHandler("note", note_embedding))
    #app.add_handler(CommandHandler("search", faiss_search))
    app.add_handler(CommandHandler("addrecord", add_record))
    app.add_handler(CommandHandler("deleterecord", delete))
    app.add_handler(CommandHandler("last", last))
    app.add_handler(CommandHandler("total", total))
    #app.add_handler(MessageHandler(filters.VOICE, transcript_voice))
    app.add_error_handler(error_handler)

    log.info("Bot is running")
    app.run_polling()
