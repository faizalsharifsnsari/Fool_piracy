import sqlite3

DB_NAME = "licenses.db"


licenses = [
    (
        "AAAA-BBBB-CCCC-DDDD",
        "701b654ca7db4312802198380263d8c00847d8fc60ba47cfa14a3af072dc3b13",
        "QWER-TYUI-OPAS-DFGH",
        None,
    ),
    (
        "EEEE-FFFF-GGGG-HHHH",
        "be7f9aa1c374c2516730b0b083dc3e436c0f982d4db4638bfaf1c2db6059d94d",
        "ZXCV-BNMK-LKJH-GFDS",
        None,
    ),
    (
        "IIII-JJJJ-KKKK-LLLL",
        "dd4fba312b33c8db6b43a86cb8a7d87b2db8c1c1bbcb9d2d71e1a4a9fa93b002",
        "POIU-YTRE-WQAS-DFGH",
        None,
    ),
]


def create_db():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        license_key TEXT PRIMARY KEY,
        exe_hash TEXT NOT NULL,
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
