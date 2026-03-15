import sqlite3

conn = sqlite3.connect("licenses.db")
cursor = conn.cursor()

for row in cursor.execute("SELECT * FROM licenses"):
    print(row)

conn.close()
