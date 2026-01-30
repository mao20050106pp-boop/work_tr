import sqlite3
from googleapiclient.discovery import build
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()


# --- 設定 ---
YOUTUBE_API_key = os.getenv("YOUTUBE_API_key")
CHANNEL_ID = "UCoW8qQy80mKH0RJTKAK-nNA"

def get_video_list():
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_key)
    ch_request = youtube.channels().list(part="contentDetails", id=CHANNEL_ID)
    ch_response = ch_request.execute()
    upload_list_id = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    v_request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=upload_list_id,
        maxResults=10
    )
    v_response = v_request.execute()

    videos = []
    for item in v_response['items']:
        vid = item['contentDetails']['videoId']
        
        # --- 【重要】動画の「実際の開始時間」を詳しく取得する ---
        video_details = youtube.videos().list(
            part="liveStreamingDetails,snippet",
            id=vid
        ).execute()
        
        details = video_details['items'][0]
        # 配信中・アーカイブなら actualStartTime、動画投稿なら publishedAt を使う
        live_details = details.get('liveStreamingDetails', {})
        start_time = live_details.get('actualStartTime', details['snippet']['publishedAt'])
        
        videos.append({
            'title': item['snippet']['title'],
            'video_id': vid,
            'start_time': start_time 
        })
    return videos

def link_matches_to_videos():
    video_list = get_video_list()
    conn = sqlite3.connect('lol_app.db')
    cursor = conn.cursor()

    # URLがNULLの試合を取得
    cursor.execute("SELECT match_id, game_start FROM match_records WHERE video_url IS NULL")
    matches = cursor.fetchall()

    if not matches:
        print("紐付けが必要な新しい試合はありません。")
        return

    for m_id, g_start_ms in matches:
        game_start_dt = datetime.fromtimestamp(g_start_ms / 1000, tz=timezone.utc)
        print(f"\n[チェック中] 試合ID: {m_id}")

        for video in video_list:
            # start_time を使うように変更
            v_start_dt = datetime.strptime(video['start_time'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            time_diff = (game_start_dt - v_start_dt).total_seconds()
            
            print(f"  - 動画: {video['title'][:15]}... | 差: {time_diff/3600:.1f}時間")

            # 配信開始後（プラス）かつ 12時間以内なら紐付け
            if 0 <= time_diff <= 43200: 
                start_seconds = int(time_diff)
                v_url = f"https://www.youtube.com/watch?v={video['video_id']}&t={start_seconds}s"
                
                cursor.execute("UPDATE match_records SET video_url = ? WHERE match_id = ?", (v_url, m_id))
                print(f"  🔗 紐付け成功！: {v_url}")
                break

    conn.commit()
    conn.close()

if __name__ == "__main__":
    link_matches_to_videos()