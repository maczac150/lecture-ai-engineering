# day1 演習用ディレクトリ

このリポジトリは、Streamlit と FastAPI を使用したアプリケーションの開発および演習用のディレクトリです。

演習には、「Google Colab」を使うことを想定しています。

リポジトリ内の「day1_practice.ipynb」を Google Colab で開き、演習を行なってください。

- [Open with Colab](https://colab.research.google.com/github/matsuolab/lecture-ai-engineering/blob/master/day1/day1_practice.ipynb)

## 事前準備

演習を行うにあたり、下記の 3 つのアカウントを利用します。

持っていない方は事前に準備することをおすすめします。

[1] Huggingface

1.1 https://huggingface.co/　の右上の Sign Up より登録してください。

1.2 https://huggingface.co/docs/hub/security-tokens 　を読み、アクセストークンの作り方を理解してください。

1.3 演習では gemma を利用する予定です。ライセンス登録など必要な準備を済ませておいてください。

https://huggingface.co/google/gemma-2-2b-jpn-it 「Access Gemma on Hugging Face」からライセンスへの同意をする。

[2] Github

2.1 https://docs.github.com/ja/get-started/start-your-journey/creating-an-account-on-github の指示に従ってアカウントを作成してください。

[3] ngrok

3.1 https://dashboard.ngrok.com/signup よりアカウントを作成してください。

3.2 https://dashboard.ngrok.com/get-started/your-authtoken より認証済みトークンが取得できることを確認してください。

## ディレクトリ構成

以下の 3 つの主要なディレクトリに分かれています。

### 01_streamlit_UI

Streamlit の基本的な UI 要素を学ぶためのデモアプリケーションが含まれています。

- **`app.py`**: Streamlit の基本的な UI 要素やレイアウトを試すためのサンプルコード。
- **`requirements.txt`**: このアプリケーションを実行するために必要な Python パッケージ。

### 02_streamlit_app

Streamlit を使用した LLM（大規模言語モデル）ベースのチャットボットアプリケーションが含まれています。

- **`app.py`**: アプリケーションのエントリーポイント。チャット機能、履歴閲覧、サンプルデータ管理の UI を提供します。
- **`ui.py`**: チャットページや履歴閲覧ページなど、アプリケーションの UI ロジックを管理します。
- **`llm.py`**: LLM モデルのロードとテキスト生成を行うモジュール。
- **`database.py`**: SQLite データベースを使用してチャット履歴やフィードバックを保存・管理します。
- **`metrics.py`**: BLEU スコアやコサイン類似度など、回答の評価指標を計算するモジュール。
- **`data.py`**: サンプルデータの作成やデータベースの初期化を行うモジュール。
- **`config.py`**: アプリケーションの設定（モデル名やデータベースファイル名）を管理します。
- **`requirements.txt`**: このアプリケーションを実行するために必要な Python パッケージ。

### 03_FastAPI

FastAPI を使用し、ローカル LLM を API サービス化する内容が含まれています。

- **`app.py`**: FastAPI を使用して LLM モデルを提供する API サーバー。モデルのロード、テキスト生成、ヘルスチェック機能を提供します。
- **`python-client.py`**: FastAPI で提供される API を利用する Python クライアントのサンプルコード。
- **`requirements.txt`**: このアプリケーションを実行するために必要な Python パッケージ。

## セットアップと実行方法

### 1. 必要な依存関係のインストール

各ディレクトリに移動し、`requirements.txt` を使用して必要なパッケージをインストールしてください。

```bash
# 例: 01_streamlit_UI の依存関係をインストール
cd 01_streamlit_UI
pip install -r requirements.txt
```

### 2. アプリケーションの実行

#### Streamlit アプリケーション

01_streamlit_UI または 02_streamlit_app ディレクトリで以下を実行します。

```bash
streamlit run app.py
```

#### FastAPI アプリケーション

03_FastAPI ディレクトリで以下を実行します。

```bash
python app.py
```

### 3. API クライアントの使用

03_FastAPI/python-client.py を実行して、FastAPI で提供される API を利用できます。

```bash
python python-client.py
```

## 使用技術

- Streamlit: インタラクティブな Web アプリケーションを簡単に構築するためのフレームワーク。
- FastAPI: 高速な API を構築するための Python フレームワーク。
- Transformers: LLM モデルのロードとテキスト生成を行うライブラリ。
- SQLite: チャット履歴やフィードバックを保存するための軽量データベース。
- Pyngrok: ローカルサーバーをインターネットに公開するためのツール。

## 注意事項

- FastAPI アプリケーションで使用するモデルは、config.py に指定されたモデル名（例: google/gemma-2-2b-jpn-it）を使用します。モデルのサイズや必要なリソースに注意してください。
- Streamlit アプリケーションでは、フィードバック機能を使用してモデルの回答を評価できます。

## 第一回講義課題での修正内容

以下の 3 つの改善を実装しました：

### 1. モデルの変更

- **変更前**: `google/gemma-2-2b-jpn-it`
- **変更後**: `mistralai/Mixtral-8x7B-Instruct-v0.1`

Mixtral 8x7B は、ミックスオブエキスパート（MoE）アーキテクチャを採用した高性能なモデルで、日本語を含む多言語対応が強化されています。文脈理解能力が向上し、より自然な応答が可能になります。

### 2. バッチサービングの実装

FastAPI アプリケーションに以下の機能を追加しました：

- **バッチ処理キュー**: リクエストをキューに蓄積し、一定数または一定時間ごとにバッチ処理
- **非同期処理**: スレッドベースの非同期処理で応答性を維持
- **バッチ処理 API**: 複数リクエストを一括処理するエンドポイント
  - `/batch/submit`: バッチリクエストの送信
  - `/batch/result/{request_id}`: 結果の取得
  - `/batch/status`: バッチ処理の状態確認

### 3. UI の改良

Streamlit UI を完全にリニューアルし、モダンなデザインと機能を追加しました：

- **モダンなデザイン**:

  - カスタム CSS によるスタイリング
  - カードベースのレイアウト
  - ダークモード対応

- **機能拡張**:

  - チャットインターフェース
  - バッチ処理管理画面
  - 分析ダッシュボード
  - 設定画面

- **ダッシュボード機能**:
  - リアルタイム処理状況の可視化
  - バッチ処理のステータス表示
  - グラフによるデータ分析

### 修正後の動作確認方法

各アプリケーションは以下のコマンドで起動できます：

```bash
# Streamlit UI
cd day1/01_streamlit_UI
pip install -r requirements.txt
streamlit run app.py

# Streamlit App
cd day1/02_streamlit_app
pip install -r requirements.txt
streamlit run app.py

# FastAPI
cd day1/03_FastAPI
pip install -r requirements.txt
python app.py
```

FastAPI サーバーが起動したら、Streamlit UI から API の URL を設定して接続することで、チャット機能やバッチ処理機能を利用できます。
