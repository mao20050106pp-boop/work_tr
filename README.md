# LoL Stream Archive Analyzer

## 概要
### LoL（League of Legends）配信者の試合データと配信アーカイブを自動で紐付ける分析ツールです。 Riot APIから取得した戦績データと、YouTube/Twitch APIから取得したアーカイブ情報を照合し、「あの配信のあの試合」をすぐに特定できます。
---

## 主な機能

### マルチプラットフォーム対応
- Riot API: 試合詳細データ（チャンピオン、KDA、勝敗）を取得
- YouTube Data API: 配信開始時刻を取得し、試合時間と自動照合
- Twitch API (開発中): 配信ステータスの取得とアーカイブ連携

### 分析・統計
- チャンピオン別の使用回数・勝率・平均KDAの自動算出
- 配信アーカイブURLへのダイレクトリンク生成

### Web画面表示（Flask）
- 直感的に戦績を確認できるダッシュボード
- チャンピオンアイコンの動的表示（Data Dragon連携）

---

## 使用技術
- Language: Python 3.x
- Framework: Flask
- Database: SQLite3 
- APIs:
  - Riot Games API
  - YouTube Data API v3
  - Twitch API (Helix)
- Libraries:
  - requests: HTTP通信
  - google-api-python-client: YouTube連携
  - python-dotenv: 環境変数管理

---

## 工夫した点
- 高精度な紐付けロジック: 配信の actualStartTime（実際の開始時刻）を基準に、試合開始時刻との差分を計算。配信外の試合が混入しないよう判定ロジックを最適化しています。

- モジュール化: データベース操作、API通信、Web表示を分離し、メンテナンス性を向上させました。

- 最新版への追従: LoLのパッチ更新に合わせて最新のチャンピオン画像を取得できるよう、Data Dragon APIのバージョン管理を考慮しています。
---


## 補足

本プロジェクトは学習目的で作成しており、
一部のコードは AI を活用しながら、
処理内容を理解・修正した上で実装しています。

---

## 実行方法（簡易）
1. 必要なライブラリをインストール
ターミナルで以下のコマンドを実行してください。
```bash
pip install flask requests google-api-python-client python-dotenv
```

2. 環境変数の準備
ルートディレクトリに .env ファイルを作成し、各種APIキーを設定してください。
```Plaintext
RIOT_API_KEY=RGAPI-xxxx-xxxx
YOUTUBE_API_KEY=AIza-xxxx-xxxx
TWITCH_CLIENT_ID=xxxx
TWITCH_CLIENT_SECRET=xxxx
```

3. アプリケーションの起動
```Bash
python app.py
```
