import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'lol_app_v2.db')

def add_valorant_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # VALORANTの試合データを保存するテーブル
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS valo_matches (
            match_id TEXT PRIMARY KEY,
            user_id INTEGER,
            agent_name TEXT,
            map_name TEXT,
            kills INTEGER,
            deaths INTEGER,
            assists INTEGER,
            win INTEGER,
            game_start_timestamp INTEGER,
            video_url TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("VALORANT用のテーブルを作成しました！")

if __name__ == "__main__":
    add_valorant_table()