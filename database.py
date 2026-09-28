import sqlite3


def create_database():

    connection = sqlite3.connect("bot.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_user_language(user_id, language):

    connection = sqlite3.connect("bot.db")

    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, language)
        VALUES (?, ?)
    """, (user_id, language))

    connection.commit()
    connection.close()


def get_user_language(user_id):

    connection = sqlite3.connect("bot.db")

    cursor = connection.cursor()

    cursor.execute(
        "SELECT language FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return None


def get_all_users():

    connection = sqlite3.connect("bot.db")

    cursor = connection.cursor()

    cursor.execute("SELECT user_id FROM users")

    users = cursor.fetchall()

    connection.close()

    return users


def get_user_count():

    connection = sqlite3.connect("bot.db")

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")

    count = cursor.fetchone()[0]

    connection.close()

    return count


def get_users():

    connection = sqlite3.connect("bot.db")

    cursor = connection.cursor()

    cursor.execute("SELECT user_id, language FROM users")

    users = cursor.fetchall()

    connection.close()

    return users