import os
import requests
from dotenv import load_dotenv

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

# あなたのPUUID（または登録した誰かのPUUID）をここに入れてテスト
# 前回のDBから誰か一人のPUUIDをコピーして貼り付けてみてください
TEST_PUUID = "ここにPUUIDをコピペ" 

def test_valo_api():
    # VALORANTの試合IDリストを取得するエンドポイント
    url = f"https://asia.api.riotgames.com/val/match/v1/matchlists/by-puuid/{TEST_PUUID}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ 成功！VALORANTのデータが取得可能です。")
        print(response.json())
    elif response.status_code == 403:
        print("❌ 権限エラー：今のAPIキーではVALORANTのデータは見れないようです。")
    else:
        print(f"⚠️ その他のエラー：{response.status_code}")

if __name__ == "__main__":
    test_valo_api()