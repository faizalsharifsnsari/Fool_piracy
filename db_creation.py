import sqlite3

DB_NAME = "licenses.db"


licenses = [
    ("AAAA-BBBB-CCCC-DDDD", None, "QWER-TYUI-OPAS-DFGH", None),
    ("EEEE-FFFF-GGGG-HHHH", None, "ZXCV-BNMK-LKJH-GFDS", None),
    ("IIII-JJJJ-KKKK-LLLL", None, "POIU-YTRE-WQAS-DFGH", None),
]


def create_db():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        license_key TEXT PRIMARY KEY,
        exe_hash TEXT,
        activation_key TEXT NOT NULL,
        fingerprint_hash TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS activation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT,
        fingerprint_hash TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    print("Database tables created")


def insert_licenses():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.executemany(
        """
        INSERT OR IGNORE INTO licenses
        (license_key, exe_hash, activation_key, fingerprint_hash)
        VALUES (?, ?, ?, ?)
        """,
        licenses,
    )

    conn.commit()
    conn.close()

    print("Licenses inserted successfully")


if __name__ == "__main__":
    create_db()
    insert_licenses()