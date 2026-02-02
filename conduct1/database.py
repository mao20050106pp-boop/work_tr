import sqlite3

def setup_database():
    # 1. データベースファイルを作成（または開く）
    # 実行すると、同じフォルダに 'lol_app.db' というファイルが自動生成されます
    conn = sqlite3.connect('lol_app.db')
    cursor = conn.cursor()

    # 2. テーブル（表）を作成
    # 既に作ってある場合は何もしないように "IF NOT EXISTS" をつけます
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_records (
            match_id TEXT PRIMARY KEY,
            champion TEXT,
            kills INTEGER,
            deaths INTEGER,
            assists INTEGER,
            win INTEGER,
            game_start INTEGER,
            video_url TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベースとテーブルの準備が完了しました！")

# 実行
setup_database()