
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