import requests
import os 
from dotenv import load_dotenv

load_dotenv()



Riot_API_key = os.getenv("RIOT_API_key") #取得した　APIキー
Riot_ID = 'tornado3'
Tag_line = 'JP0'
Region = 'asia'

def get_puuid(Riot_ID, Tag_line):
    url = f'https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/tornado3/JP0'
    headers = {'X-Riot-Token': Riot_API_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()['puuid']
    else:
        print(f'エラーが発生しました: {response.status_code}')
        return None


puuid = get_puuid(Riot_ID, Tag_line)
if puuid:
    print(f"PUUIDの取得に成功しました\n{puuid}")


def get_match_ids(puuid, count=5):
    # 変数を { } で囲むことで、中身が展開されます
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    headers = {"X-Riot-Token": Riot_API_key} # 変数名は作成した名前に合わせてください
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        # ここも { } を付けて中身を表示
        print(f"試合ID取得エラー: {response.status_code}")
        return []

if puuid:
    # {puuid} と書くことで、本物のIDが表示されます
    print(f"PUUID取得成功: {puuid}")
    match_ids = get_match_ids(puuid)
    print(f"直近の試合ID: {match_ids}")


def get_match_detail(match_id):
    # 試合の具体的な中身（統計）を取るためのURL
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": Riot_API_key}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"試合詳細取得エラー: {response.status_code}")
        return None

# --- 実行部分の続き ---
if match_ids:
    # リストの一番最初（最新）の試合IDを使ってみる
    target_match = match_ids[0]
    print(f"\n最新の試合 {target_match} のデータを解析中...")
    
    detail = get_match_detail(target_match)
    
    if detail:
        # 参加者全員のデータの中から、自分のPUUIDに一致する人を探す
        participants = detail['info']['participants']
        duration_seconds = detail['info']['gameDuration']
        minutes = duration_seconds // 60


        for p in participants:
            if p['puuid'] == puuid:
                champion = p['championName']
                cs = p['totalMinionsKilled'] + p['neutralMinionsKilled']
                cs_per_m = cs / minutes
                k = p['kills']
                d = p['deaths']
                a = p['assists']
                win = "勝利" if p['win'] else "敗北"
                

                print(f"【試合結果】")
                print(f"使用チャンピオン: {champion}")
                print(f"分間CS: {cs_per_m}")
                print(f"スコア: {k}/{d}/{a}")
                print(f"結果: {win}")