# tracker.py
# Финансовый + Food трекер

from db import cursor, connection
from telegram import Update
from telegram.ext import ContextTypes


async def add_record(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.replace("/addrecord", "").strip()

    if "a:" not in text:
        await update.message.reply_text("Нет суммы (a:), давай нормально")
        return

    try:
        # сумма
        a_index = text.index("a:")
        after_a = text[a_index + 2:].strip()
        amount = int(after_a.split()[0])

        rest = after_a.split(None, 1)[1]

        # описание (между суммой и desc:)
        if "desc:" not in rest:
            await update.message.reply_text("Нет desc:")
            return

        desc_index = rest.index("desc:")
        name = rest[:desc_index].strip()
        rest2 = rest[desc_index:]

        description = rest2.split("desc:")[1].split("cat:")[0].strip()

        # категория
        if "cat:" not in rest2:
            await update.message.reply_text("Нет cat:")
            return

        category = rest2.split("cat:")[1].split("acc:")[0].strip()

        # счёт
        if "acc:" not in rest2:
            await update.message.reply_text("Нет acc:")
            return

        account = rest2.split("acc:")[1].strip()

        cursor.execute(
            """
            INSERT INTO Finances
            (name, description, amount, category, account)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, description, amount, category, account),
        )

        connection.commit()

        await update.message.reply_text(
            f"Записал:\n"
            f"{name} | {category}\n"
            f"{amount}₸ → {account}\n"
            f"{description}"
        )

    except Exception as e:
        await update.message.reply_text(f"Кривой формат \n{e}")


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Формат: /delete ID")
        return

    record_id = context.args[0]

    cursor.execute("DELETE FROM Finances WHERE id=?", (record_id,))
    connection.commit()

    await update.message.reply_text("Удалено!")


async def last(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("""
        SELECT id, name, amount, account, created_at
        FROM Finances
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text("Пока записей нет")
        return

    text = ""
    for r in rows:
        text += f"{r[0]} | {r[2]}₸ | {r[1]} | {r[3]} | {r[4]}\n"

    await update.message.reply_text(text)


async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
    total_sum = cursor.fetchone()[0]

    await update.message.reply_text(f"{text}\nвсего: {total_sum}₸")



async def addfood(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.replace("/addfood", "").strip()

    if "c:" not in text:
        await update.message.reply_text("Нет калорий (c:)")
        return

    try:
        # калории
        c_index = text.index("c:")
        after_c = text[c_index + 2:].strip()
        calories = int(after_c.split()[0])

        name_part = after_c.split(None, 1)[1]

        pr_index = name_part.index("pr:")
        name = name_part[:pr_index].strip()
        rest = name_part[pr_index:]

        protein = float(rest.split("pr:")[1].split()[0])

        fat = 0
        if "f:" in rest:
            fat = float(rest.split("f:")[1].split()[0])

        carbs = 0
        if "cbs:" in rest:
            carbs = float(rest.split("cbs:")[1].split()[0])

        weight = 0
        if "w:" in rest:
            weight = float(rest.split("w:")[1].split()[0])

        meal_type = "unknown"
        if "m:" in rest:
            meal_type = rest.split("m:")[1].split()[0]

        cursor.execute(
            """
            INSERT INTO FoodTracker
            (name, calories, protein, fat, carbs, weight, meal_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, calories, protein, fat, carbs, weight, meal_type),
        )

        connection.commit()

        await update.message.reply_text(
            f"Добавил:\n"
            f"{name} ({meal_type})\n"
            f"{calories} kcal\n"
            f"Б:{protein} Ж:{fat} У:{carbs}\n"
            f"{weight} г"
        )

    except Exception as e:
        await update.message.reply_text(f"Кривой формат \n{e}")


async def lastfood(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("""
        SELECT id, name, calories, meal_type, created_at
        FROM FoodTracker
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text("Пока ничего не ел")
        return

    text = ""
    for r in rows:
        text += f"{r[0]} | {r[1]} | {r[2]} kcal | {r[3]} | {r[4]}\n"

    await update.message.reply_text(text)


async def todaycal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("""
        SELECT SUM(calories)
        FROM FoodTracker
        WHERE date(created_at) = date('now')
    """)

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    await update.message.reply_text(f"Сегодня съел: {total} ккал")

async def deletefood(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Формат: /deletefood ID")
        return

    food_id = context.args[0]

    # проверим, существует ли запись
    cursor.execute("SELECT id, name FROM FoodTracker WHERE id=?", (food_id,))
    row = cursor.fetchone()

    if not row:
        await update.message.reply_text("Такой записи нет")
        return

    cursor.execute("DELETE FROM FoodTracker WHERE id=?", (food_id,))
    connection.commit()

    await update.message.reply_text(f"Удалил: {row[1]} (ID {row[0]})")

