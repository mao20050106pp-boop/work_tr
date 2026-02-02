from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from googleapiclient.discovery import build # APIを使うために追加
import requests # Riot API用に追加
from datetime import datetime
import requests


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_key")
RIOT_API_KEY = os.getenv("RIOT_API_KEY") # .envの名前を確認してください


app = Flask(__name__)

@app.template_filter('datetimeformat')
def datetimeformat(value):
    # ミリ秒を秒に変換して日時形式へ
    dt = datetime.fromtimestamp(value / 1000)
    return dt.strftime('%m/%d %H:%M')

# データベースのパス（同じフォルダ内を指定）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'lol_app_v2.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # 列名でデータを取り出せるようにする
    return conn

@app.route('/')
def index():
    conn = get_db()
    # 登録されているユーザー一覧を取得
    users = conn.execute('SELECT * FROM users').fetchall()

    conn.close()
    return render_template('index.html', users=users)


# --- 1. ライブ状態をチェックする関数 (app.pyのどこかに一度だけ書く) ---
def get_live_status(channel_id):
    if not channel_id:
        return "none"
    try:
        # YouTube APIで現在のライブ状況を確認
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={YOUTUBE_API_KEY}"
        res = requests.get(url).json()
        items = res.get('items', [])
        if items:
            # snippet.liveBroadcastContent が "live" であることを最終確認
            # (公開予定の場合は "upcoming" になるため、ここで弾けます)
            status = items[0].get('snippet', {}).get('liveBroadcastContent')
            if status == "live":
                return "live"
        
        return "none"
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return "none"
    
# --- 2. ユーザー詳細ページ (1つだけに絞る！) ---
@app.route('/user/<int:user_id>')
def user_detail(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    matches = conn.execute('SELECT * FROM lol_matches WHERE user_id = ? ORDER BY game_start_timestamp DESC', (user_id,)).fetchall()
    
    # ここでライブ中かどうかを判定
    # live_status は "live" か "none" になります
    live_status = get_live_status(user['youtube_ch_id'])
    
    conn.close()
    # live_status を HTML に渡す
    return render_template('user_detail.html', user=user, matches=matches, live_status=live_status)

def get_channel_id_from_url(url):
    """URLまたはハンドル名からチャンネルIDを返す"""
    if not url: return None
    
    # URLからハンドル部分（@以降）を抜き出す
    if '@' in url:
        handle = url.split('@')[-1].split('/')[0]
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # ハンドル名で検索
        request = youtube.search().list(
            part="snippet",
            q=f"@{handle}",
            type="channel",
            maxResults=1
        )
        response = request.execute()
        
        if response['items']:
            return response['items'][0]['snippet']['channelId']
            
    # すでにチャンネルID（UC...）が入力されている場合はそのまま返す
    if 'UC' in url and len(url) >= 24:
        # パスの中に含まれている場合を考慮
        import re
        match = re.search(r'(UC[\w-]{22})', url)
        return match.group(1) if match else url

    return url # 判別不能ならそのまま返す

def get_puuid(riot_id, riot_tag):
    """Riot IDとTagからPUUIDを取得する"""
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_id}/{riot_tag}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('puuid')
    else:
        print(f"PUUID取得失敗: {response.status_code}")
        return None


@app.route('/register', methods=['POST'])
def register():
    display_name = request.form['display_name']
    riot_id = request.form['riot_id']
    riot_tag = request.form['riot_tag']
    yt_url = request.form['yt_id'] # URLが送られてくる

   # 1. YouTube URL -> Channel ID 変換
    yt_id = get_channel_id_from_url(yt_url)
    # 2. Riot ID#Tag -> PUUID 変換 (新機能！)
    puuid = get_puuid(riot_id, riot_tag)

    if not puuid:
        return "PUUIDの取得に失敗しました。Riot IDとTagが正しいか確認してください。", 400

    conn = get_db()
    cursor = conn.cursor()
    # puuidも一緒に保存する
    cursor.execute('''
        INSERT INTO users (display_name, riot_id, riot_tag, puuid, youtube_ch_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (display_name, riot_id, riot_tag, puuid, yt_id))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


def get_live_status(channel_id):
    if not channel_id:
        return "none"
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={os.getenv('YOUTUBE_API_key')}"
        res = requests.get(url).json()
        # 本当にライブ中の動画があれば 'live' を返す
        if res.get('items'):
            return "live"
    except:
        pass
    return "none"


if __name__ == '__main__':
    app.run(debug=True)