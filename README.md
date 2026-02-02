# LoL Stream Archive Analyzer

## 概要
LoL（League of Legends）配信者が過去に行った試合を、
Riot API から取得した試合履歴と
YouTube API から取得した配信アーカイブを紐付けて管理・分析するWebアプリです。

過去の配信内で「どのチャンピオンを使っていたか」を
すぐに確認・統計表示し、該当する配信アーカイブを視聴できます。

---

## 主な機能

### データ取得
- Riot API を使用して試合履歴を取得
  - YouTube Data API を使用して配信アーカイブを取得

### データ保存
以下の情報を SQLite に保存しています。
- 試合ID
- 試合日時
- 使用チャンピオン
- 勝敗
- K/D/A
- 配信アーカイブURL

### 分析機能
- チャンピオン使用回数ランキング
- チャンピオン別勝率
- 平均KDAの算出

### Web画面表示（Flask）
- 試合一覧表示
- チャンピオン別統計表示
- 配信アーカイブへのリンク表示

---

## 使用技術
- Python
- Flask
- SQLite
- Riot Games API
- YouTube Data API
- python-dotenv

---

## 工夫した点
- 配信動画の `actualStartTime` を優先的に使用し、
  配信開始時刻と試合開始時刻のズレを考慮して紐付けを行っています
- 配信開始後から一定時間内の試合のみを対象とすることで、
  誤った動画紐付けを防いでいます
- データ取得・分析・表示を役割ごとに分離して実装しています

---


## 補足

本プロジェクトは学習目的で作成しており、
一部のコードは AI を活用しながら、
処理内容を理解・修正した上で実装しています。

---

1. 必要なライブラリをインストール
ターミナルで以下のコマンドを実行してください。
```bash
pip install flask requests google-api-python-client python-dotenv
```

2. 環境変数の準備
ルートディレクトリに .env ファイルを作成し、各種APIキーを設定してください。

RIOT_API_KEY=RGAPI-xxxx-xxxx
YOUTUBE_API_KEY=AIza-xxxx-xxxx
TWITCH_CLIENT_ID=xxxx
TWITCH_CLIENT_SECRET=xxxx


3. アプリケーションの起動
```Bash
python app.py
```

---

##補足
本プロジェクトは学習目的で作成しています。AIを活用したコード生成を取り入れつつ、デバッグやロジックのカスタマイズはすべて自身で行い、各APIの仕様やデータ構造を深く理解した上で実装しています。
