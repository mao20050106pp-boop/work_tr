import sqlite3

conn = sqlite3.connect('lol_app.db')
cursor = conn.cursor()

# DBの中身を全部表示
cursor.execute("SELECT * FROM match_records")
rows = cursor.fetchall()

print("--- 現在DBに保存されているデータ ---")
for row in rows:
    print(row)

conn.close()