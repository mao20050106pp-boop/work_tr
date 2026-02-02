import os
import sqlite3
import requests
from googleapiclient.discovery import build
import re
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# 設定
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_key")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'lol_app_v2.db')

def get_db():
    return sqlite3.connect(DB_PATH)

# --- 以前作った YouTube 時間計算ロジックなどの関数をここに集約 ---
def parse_duration(duration_str):
    # もし解析できない文字が入ってきてもエラーにならないようにガード
    match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds
def update_user_matches(user_id, puuid, yt_ch_id):
    # 1. LoLの最新5試合を取得
    match_ids_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=5"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    match_ids = requests.get(match_ids_url, headers=headers).json()

    conn = get_db()
    
    # 2. 各試合の詳細を取得して保存
    for m_id in match_ids:
        detail_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{m_id}"
        detail = requests.get(detail_url, headers=headers).json()
        
        # 自分のデータを探す
        me = next(p for p in detail['info']['participants'] if p['puuid'] == puuid)
        
        # 試合データを保存 (INSERT OR IGNORE で重複回避)
        conn.execute('''
            INSERT OR IGNORE INTO lol_matches 
            (match_id, user_id, champion_name, kills, deaths, assists, win, game_duration_sec, game_start_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            m_id, user_id, me['championName'], me['kills'], me['deaths'], me['assists'],
            1 if me['win'] else 0, detail['info']['gameDuration'], detail['info']['gameStartTimestamp']
        ))
    
    conn.commit()

    # 3. YouTubeアーカイブとの紐付け (以前の link_data.py のロジック)
    if yt_ch_id:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        # チャンネルの最新動画を取得
        res = youtube.search().list(channelId=yt_ch_id, part="snippet", order="date", maxResults=5, type="video").execute()
        
        for item in res.get('items', []):
            v_id = item['id']['videoId']
            v_detail = youtube.videos().list(id=v_id, part="liveStreamingDetails,contentDetails").execute()['items'][0]
            
            if 'liveStreamingDetails' in v_detail:
                start_time_str = v_detail['liveStreamingDetails']['actualStartTime']
                start_dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                v_start_ts = int(start_dt.timestamp() * 1000)
                v_duration = parse_duration(v_detail['contentDetails']['duration'])

                # DB内の「まだURLがない試合」と照合
                matches = conn.execute('SELECT match_id, game_start_timestamp FROM lol_matches WHERE user_id = ? AND video_url IS NULL', (user_id,)).fetchall()
                for m_id, m_ts in matches:
                    offset = (m_ts - v_start_ts) // 1000
                    if 0 < offset < v_duration:
                        video_url = f"https://www.youtube.com/watch?v={v_id}&t={max(0, offset-60)}s"
                        conn.execute('UPDATE lol_matches SET video_url = ? WHERE match_id = ?', (video_url, m_id))

    conn.commit()
    conn.close()

def main():
    conn = get_db()
    users = conn.execute('SELECT user_id, display_name, puuid, youtube_ch_id FROM users').fetchall()
    conn.close()

    for u_id, name, puuid, yt_id in users:
        print(f"【{name}】のデータを更新中...")
        if puuid:
            update_user_matches(u_id, puuid, yt_id)
    
    print("全ユーザーの更新が完了しました！")

if __name__ == "__main__":
    main()