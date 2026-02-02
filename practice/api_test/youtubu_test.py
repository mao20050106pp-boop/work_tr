from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()


# --- 設定 ---
YouTube_API_key = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UCoW8qQy80mKH0RJTKAK-nNA"  # 配信者のチャンネルID

def get_archives(channel_id):
    youtube = build('youtube', 'v3', developerKey=YouTube_API_key)

    # チャンネルの「アップロード済み動画」リストのIDを取得
    ch_request = youtube.channels().list(part="contentDetails", id=channel_id)
    ch_response = ch_request.execute()
    
    upload_list_id = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # 動画一覧を取得
    v_request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=upload_list_id,
        maxResults=10
    )
    v_response = v_request.execute()

    for item in v_response['items']:
        title = item['snippet']['title']
        video_id = item['contentDetails']['videoId']
        published_at = item['snippet']['publishedAt']
        print(f"タイトル: {title}")
        print(f"URL: https://www.youtube.com/watch?v={video_id}")
        print(f"公開日時: {published_at}\n---")

get_archives(CHANNEL_ID)