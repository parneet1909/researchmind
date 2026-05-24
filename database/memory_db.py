import sqlite3
import json

DB_NAME = "database/research_memory.db"

# ─────────────────────────────────────────────────────────────
# CREATE DATABASE
# ─────────────────────────────────────────────────────────────

def init_db():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            title TEXT,
            topic TEXT,
            search_result TEXT,
            reader_result TEXT,
            writer_result TEXT,
            critic_result TEXT,
            conversation TEXT,
            pdf_name TEXT,
            chat_type TEXT DEFAULT 'web',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()

    # ADD NEW COLUMNS IF OLD DATABASE EXISTS

    try:
        cursor.execute(
            "ALTER TABLE chats ADD COLUMN pdf_name TEXT"
        )
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute(
            "ALTER TABLE chats ADD COLUMN chat_type TEXT DEFAULT 'web'"
        )
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────
# SAVE CHAT
# ─────────────────────────────────────────────────────────────

def save_chat(
    user_email,
    title,
    topic,
    search_result,
    reader_result,
    writer_result,
    critic_result,
    conversation,
    pdf_name=None,
    chat_type="web"
):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chats (
            user_email,
            title,
            topic,
            search_result,
            reader_result,
            writer_result,
            critic_result,
            conversation,
            pdf_name,
            chat_type
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_email,
            title,
            topic,
            search_result,
            reader_result,
            writer_result,
            critic_result,
            json.dumps(conversation),
            pdf_name,
            chat_type
        )
    )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────
# GET SINGLE CHAT
# ─────────────────────────────────────────────────────────────

def get_chat(chat_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM chats
        WHERE id = ?
        """,
        (chat_id,)
    )

    chat = cursor.fetchone()

    conn.close()

    return chat


# ─────────────────────────────────────────────────────────────
# GET ALL CHATS
# ─────────────────────────────────────────────────────────────

def get_all_chats(user_email):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, created_at
        FROM chats
        WHERE user_email = ?
        ORDER BY id DESC
        """,
        (user_email,)
    )

    chats = cursor.fetchall()

    conn.close()

    return chats


# ─────────────────────────────────────────────────────────────
# GET PDF CHATS
# ─────────────────────────────────────────────────────────────

def get_pdf_chats(user_email):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, pdf_name, created_at
        FROM chats
        WHERE user_email = ?
        AND chat_type = 'pdf'
        ORDER BY id DESC
        """,
        (user_email,)
    )

    chats = cursor.fetchall()

    conn.close()

    return chats


# ─────────────────────────────────────────────────────────────
# UPDATE CHAT
# ─────────────────────────────────────────────────────────────

def update_chat(
    chat_id,
    topic,
    search_result,
    reader_result,
    writer_result,
    critic_result,
    conversation,
    pdf_name=None,
    chat_type="web"
):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE chats
        SET
            topic=?,
            search_result=?,
            reader_result=?,
            writer_result=?,
            critic_result=?,
            conversation=?,
            pdf_name=?,
            chat_type=?
        WHERE id=?
        """,
        (
            topic,
            search_result,
            reader_result,
            writer_result,
            critic_result,
            json.dumps(conversation),
            pdf_name,
            chat_type,
            chat_id
        )
    )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────
# DELETE CHAT
# ─────────────────────────────────────────────────────────────

def delete_chat(chat_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM chats WHERE id=?",
        (chat_id,)
    )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────
# RENAME CHAT TITLE
# ─────────────────────────────────────────────────────────────

def rename_chat(chat_id, new_title):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "UPDATE chats SET title=? WHERE id=?",
        (new_title, chat_id)
    )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────
# LOAD CONVERSATION
# ─────────────────────────────────────────────────────────────

def load_conversation(chat_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT conversation
        FROM chats
        WHERE id=?
        """,
        (chat_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row and row[0]:

        return json.loads(row[0])

    return []