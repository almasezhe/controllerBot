#tracker.py
#Финансовый трекер

from db import cursor, connection


#Database Structure
#name TEXT, description TEXT, amount INT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, account TEXT

async def add_record(update: Update, context: ContextTypes.DEFAULT_TYPE):

    args = context.args

    if len(args) < 5:
        await update.message.reply_text(
            "Формат:\n"
            "/addrecord amount name description category account"
        )
        return

    try:
        amount = int(args[0])
        name = args[1]

        account = args[-1]
        category = args[-2]

        description = " ".join(args[2:-2])

        cursor.execute(
            """
            INSERT INTO Finances 
            (name, description, amount, account, category) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, description, amount, account, category),
        )

        connection.commit()

        await update.message.reply_text(
            f"Записал:\n"
            f"{name} | {category}\n"
            f"{amount}₸ → {account}\n"
            f"{description}"
        )

    except ValueError:
        await update.message.reply_text("Сумма должна быть числом, камон")


    
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Формат: /delete ID")
        return

    id = context.args[0]

    cursor.execute("DELETE FROM Finances WHERE id=?", (id,))
    connection.commit()

    await update.message.reply_text("Удалено!")

    
async def last(update:Update,context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("""
        SELECT id, name, amount, account, created_at
        FROM Finances
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()

    out = []
    for r in rows:
        out.append(f"{r[0]} | {r[2]}₸ | {r[1]} | {r[3]} | {r[4]}")

    await update.message.reply_text("\n".join(out))

async def total(update:Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("""
        SELECT account, SUM(amount)
        FROM Finances
        GROUP BY account
    """)

    rows = cursor.fetchall()

    text = "по счетам:\n"
    for acc, s in rows:
        text += f"{acc}: {s}₸\n"

    cursor.execute("SELECT SUM(amount) FROM Finances")
    all = cursor.fetchone()[0]

    await update.message.reply_text(f"\nвсего: {all}₸")
    
