import os
import requests
import sqlite3
from dotenv import load_dotenv

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lol_app_v2.db')

def update_valo_matches(user_id, puuid):
    # VALORANTの最新試合IDリストを取得 (Asiaリージョン)
    url = f"https://asia.api.riotgames.com/val/match/v1/recent-matches/by-queue/competitive" 
    # ※実際には個人別の matchlist-v1 を使いますが、まずは通るか確認
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    # ここはRiotの権限によって挙動が変わるため、一旦枠組みだけ作ります
    print(f"ID: {user_id} のVALORANTデータをチェック中...")

    # (ここにLoL版と同じような保存ロジックを書きます)

if __name__ == "__main__":
    # 登録ユーザー全員を回る処理
    conn = sqlite3.connect(DB_PATH)
    users = conn.execute('SELECT user_id, puuid FROM users').fetchall()
    for u_id, puuid in users:
        update_valo_matches(u_id, puuid)
    conn.close()