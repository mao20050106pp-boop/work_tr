import sqlite3
import os

def init_db_v2():
    # このファイル（init_db_v2.py）があるフォルダのパスを取得
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # そのフォルダの中に lol_app_v2.db を作るように指定
    db_path = os.path.join(base_dir, 'lol_app_v2.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # --- 以下、テーブル作成コードは同じ ---

    # 1. ユーザー管理テーブル
    # pandasで結合(Merge)しやすいよう、IDを主軸にします
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        display_name TEXT NOT NULL,
        riot_id TEXT NOT NULL,
        riot_tag TEXT NOT NULL,      -- NameとTagを分けておくと集計時に便利
        puuid TEXT UNIQUE,
        youtube_ch_id TEXT,
        twitch_id TEXT
    )
    ''')

    # 2. LoL試合データテーブル
    # pandasで読み込んだ際、そのまま計算に使える型で定義します
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lol_matches (
        match_id TEXT PRIMARY KEY,
        user_id INTEGER,
        champion_name TEXT,
        kills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        win INTEGER,                 -- 1(Win) / 0(Loss) で保存すると平均がそのまま勝率になる
        game_duration_sec INTEGER,   -- 試合時間（集計で「1分あたりのキル」など出すため）
        game_start_timestamp INTEGER,
        queue_type TEXT,             -- RankかNormalか
        video_url TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    # 3. VALORANT試合データテーブル（準備）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS valo_matches (
        match_id TEXT PRIMARY KEY,
        user_id INTEGER,
        agent_name TEXT,
        kills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        score INTEGER,               -- バロ特有のスコア項目
        win INTEGER,
        game_start_timestamp INTEGER,
        video_url TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("集計対応版データベース (v2) を作成しました！")

if __name__ == "__main__":
    init_db_v2()