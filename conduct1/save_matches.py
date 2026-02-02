import sqlite3
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# --- 設定 ---
Riot_API_key = os.getenv("RIOT_API_KEY")
GAME_NAME = "tornado3"
TAG_LINE = "JP0"

# --- 1. PUUIDを取得する関数 ---
def get_my_puuid():
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{GAME_NAME}/{TAG_LINE}"
    headers = {"X-Riot-Token": Riot_API_key}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()['puuid']
    else:
        print(f"PUUID取得失敗: {res.status_code}")
        return None

# --- 2. データベースに保存する関数 ---
def save_to_db(match_data):
    conn = sqlite3.connect('lol_app.db')
    cursor = conn.cursor()
    # テーブルがなければ作成
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
    # データを保存
    cursor.execute('''
        INSERT OR IGNORE INTO match_records 
        (match_id, champion, kills, deaths, assists, win, game_start)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', match_data)
    conn.commit()
    conn.close()

# --- 3. メイン処理：試合情報を取ってきてDBへ ---
def collect_latest_matches():
    puuid = get_my_puuid()
    if not puuid: return

    print(f"🔍 {GAME_NAME}#{TAG_LINE} のデータを取得中...")
    headers = {"X-Riot-Token": Riot_API_key}
    
    # 最新5試合のIDを取得
    match_list_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20"
    res = requests.get(match_list_url, headers=headers)
    if res.status_code != 200: return
    
    match_ids = res.json()
    
    for m_id in match_ids:
        # 各試合の詳細を取得
        detail_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{m_id}"
        detail_res = requests.get(detail_url, headers=headers)
        if detail_res.status_code != 200: continue
        
        detail = detail_res.json()
        participants = detail['info']['participants']
        
        for p in participants:
            if p['puuid'] == puuid:
                match_data = (
                    m_id,
                    p['championName'],
                    p['kills'],
                    p['deaths'],
                    p['assists'],
                    1 if p['win'] else 0,
                    detail['info']['gameStartTimestamp']
                )
                save_to_db(match_data)
                print(f"✅ 保存完了: {m_id} | 使用キャラ: {p['championName']}")

# 実行
if __name__ == "__main__":
    collect_latest_matches()