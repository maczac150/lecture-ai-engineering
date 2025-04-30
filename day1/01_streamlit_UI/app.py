import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import json
import random
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ============================================
# ページ設定
# ============================================
st.set_page_config(
    page_title="AI Assistant Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    /* メインコンテンツのスタイル */
    .main {
        background-color: #f8f9fa;
    }
    
    /* ヘッダーのスタイル */
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #1E3A8A !important;
        margin-bottom: 1rem !important;
    }
    
    /* サブヘッダーのスタイル */
    .sub-header {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #2563EB !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* カードのスタイル */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* メトリクスのスタイル */
    .metric-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    
    .metric-card {
        background-color: #EFF6FF;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        flex: 1;
        min-width: 120px;
    }
    
    .metric-value {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #1E40AF !important;
    }
    
    .metric-label {
        font-size: 0.9rem !important;
        color: #6B7280 !important;
    }
    
    /* ボタンのスタイル */
    .stButton > button {
        background-color: #2563EB;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: #1D4ED8;
    }
    
    /* タブのスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #E5E7EB;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        height: auto;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: white !important;
    }
    
    /* テキストエリアのスタイル */
    .stTextArea textarea {
        border-radius: 5px;
        border: 1px solid #D1D5DB;
    }
    
    /* サイドバーのスタイル */
    .sidebar .sidebar-content {
        background-color: #1E3A8A;
    }
    
    /* アニメーション */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* ダークモード対応 */
    @media (prefers-color-scheme: dark) {
        .main {
            background-color: #1F2937;
        }
        
        .card {
            background-color: #374151;
        }
        
        .metric-card {
            background-color: #1F2937;
        }
        
        .metric-value {
            color: #60A5FA !important;
        }
        
        .metric-label {
            color: #9CA3AF !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# セッション状態の初期化
# ============================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'batch_requests' not in st.session_state:
    st.session_state.batch_requests = []

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8501"

# ============================================
# サイドバー
# ============================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.markdown("<h1 style='color: #60A5FA;'>AI Assistant</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ナビゲーション
    page = st.radio(
        "ナビゲーション",
        ["チャット", "バッチ処理", "分析ダッシュボード", "設定"],
        key="navigation"
    )
    
    st.markdown("---")
    
    # API接続状態
    try:
        response = requests.get(f"{st.session_state.api_url}/health", timeout=2)
        if response.status_code == 200:
            st.success("API接続: オンライン")
            api_info = response.json()
            st.info(f"モデル: {api_info['details']['model_name']}")
        else:
            st.error("API接続: エラー")
    except:
        st.error("API接続: オフライン")
    
    # ダークモード切替
    dark_mode = st.checkbox("ダークモード", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.experimental_rerun()
    
    st.markdown("---")
    st.caption("© 2025 AI Assistant Dashboard")

# ============================================
# メイン機能
# ============================================

# チャットページ
if page == "チャット":
    st.markdown("<h1 class='main-header'>AI アシスタント</h1>", unsafe_allow_html=True)
    
    # チャット履歴の表示
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if st.session_state.chat_history:
        for i, (role, content) in enumerate(st.session_state.chat_history):
            if role == "user":
                st.markdown(f"<div style='background-color: #EFF6FF; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>あなた:</strong> {content}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color: #F0FDF4; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>AI:</strong> {content}</div>", unsafe_allow_html=True)
    else:
        st.info("会話を始めるには、メッセージを入力してください。")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 入力フォーム
    with st.form("chat_form"):
        user_input = st.text_area("メッセージを入力", height=100)
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.form_submit_button("送信")
        with col2:
            st.markdown("音声入力や高度な設定は設定タブから行えます。")
    
    # 送信ボタンが押された場合
    if submit_button and user_input:
        # ユーザーの入力をチャット履歴に追加
        st.session_state.chat_history.append(("user", user_input))
        
        # APIリクエストの準備
        try:
            with st.spinner("AI が回答を生成中..."):
                # APIリクエスト
                response = requests.post(
                    f"{st.session_state.api_url}/generate",
                    json={"prompt": user_input, "max_new_tokens": 512}
                )
                
                if response.status_code == 200:
                    ai_response = response.json()["generated_text"]
                    # AIの応答をチャット履歴に追加
                    st.session_state.chat_history.append(("assistant", ai_response))
                else:
                    st.error(f"エラー: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"APIリクエスト中にエラーが発生しました: {e}")
        
        # 画面を再読み込みして最新の会話を表示
        st.experimental_rerun()

# バッチ処理ページ
elif page == "バッチ処理":
    st.markdown("<h1 class='main-header'>バッチ処理</h1>", unsafe_allow_html=True)
    
    # バッチ処理の説明
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<p>バッチ処理では、複数のリクエストをまとめて処理できます。効率的に大量のテキスト生成を行いたい場合に便利です。</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # バッチ処理のステータス
    st.markdown("<h2 class='sub-header'>バッチ処理ステータス</h2>", unsafe_allow_html=True)
    
    try:
        status_response = requests.get(f"{st.session_state.api_url}/batch/status")
        if status_response.status_code == 200:
            status = status_response.json()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("キューサイズ", status["queue_size"])
            with col2:
                st.metric("処理中", "はい" if status["processing"] else "いいえ")
            with col3:
                st.metric("待機中の結果", status["results_waiting"])
        else:
            st.error("バッチ処理ステータスの取得に失敗しました")
    except:
        st.error("バッチ処理サービスに接続できません")
    
    # 新しいバッチリクエスト
    st.markdown("<h2 class='sub-header'>新しいバッチリクエスト</h2>", unsafe_allow_html=True)
    
    with st.form("batch_form"):
        batch_input = st.text_area("プロンプト", height=100)
        col1, col2 = st.columns(2)
        with col1:
            max_tokens = st.slider("最大トークン数", 50, 1000, 512)
        with col2:
            temperature = st.slider("温度", 0.0, 1.0, 0.7)
        
        submit_batch = st.form_submit_button("バッチリクエストを送信")
    
    if submit_batch and batch_input:
        try:
            # バッチリクエストを送信
            batch_response = requests.post(
                f"{st.session_state.api_url}/batch/submit",
                json={
                    "prompt": batch_input,
                    "params": {
                        "max_new_tokens": max_tokens,
                        "temperature": temperature
                    }
                }
            )
            
            if batch_response.status_code == 200:
                result = batch_response.json()
                request_id = result["request_id"]
                
                # リクエスト情報を保存
                st.session_state.batch_requests.append({
                    "id": request_id,
                    "prompt": batch_input,
                    "status": "queued",
                    "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "result": None
                })
                
                st.success(f"バッチリクエストが送信されました。リクエストID: {request_id}")
            else:
                st.error(f"バッチリクエストの送信に失敗しました: {batch_response.text}")
        except Exception as e:
            st.error(f"バッチリクエスト中にエラーが発生しました: {e}")
    
    # バッチリクエスト一覧
    st.markdown("<h2 class='sub-header'>バッチリクエスト一覧</h2>", unsafe_allow_html=True)
    
    if not st.session_state.batch_requests:
        st.info("バッチリクエストはまだありません")
    else:
        # リクエストの状態を更新
        for i, request in enumerate(st.session_state.batch_requests):
            if request["status"] in ["queued", "pending"]:
                try:
                    result_response = requests.get(
                        f"{st.session_state.api_url}/batch/result/{request['id']}",
                        params={"wait": False}
                    )
                    
                    if result_response.status_code == 200:
                        result = result_response.json()
                        st.session_state.batch_requests[i]["status"] = result["status"]
                        
                        if result["status"] == "completed":
                            st.session_state.batch_requests[i]["result"] = result["result"]["generated_text"]
                        elif result["status"] == "error":
                            st.session_state.batch_requests[i]["result"] = f"エラー: {result['error']}"
                except:
                    pass
        
        # リクエスト一覧を表示
        for i, request in enumerate(st.session_state.batch_requests):
            with st.expander(f"リクエスト {i+1}: {request['submitted_at']} - {request['status'].upper()}"):
                st.markdown(f"**プロンプト:** {request['prompt']}")
                st.markdown(f"**ステータス:** {request['status']}")
                st.markdown(f"**リクエストID:** {request['id']}")
                
                if request["result"]:
                    st.markdown("**結果:**")
                    st.markdown(f"{request['result']}")
                elif request["status"] in ["queued", "pending"]:
                    if st.button(f"結果を取得", key=f"get_result_{i}"):
                        try:
                            result_response = requests.get(
                                f"{st.session_state.api_url}/batch/result/{request['id']}",
                                params={"wait": True, "timeout": 10.0}
                            )
                            
                            if result_response.status_code == 200:
                                result = result_response.json()
                                st.session_state.batch_requests[i]["status"] = result["status"]
                                
                                if result["status"] == "completed":
                                    st.session_state.batch_requests[i]["result"] = result["result"]["generated_text"]
                                    st.success("結果を取得しました")
                                    st.experimental_rerun()
                                elif result["status"] == "error":
                                    st.session_state.batch_requests[i]["result"] = f"エラー: {result['error']}"
                                    st.error("エラーが発生しました")
                                    st.experimental_rerun()
                                else:
                                    st.info("結果はまだ利用できません")
                        except Exception as e:
                            st.error(f"結果の取得中にエラーが発生しました: {e}")

# 分析ダッシュボードページ
elif page == "分析ダッシュボード":
    st.markdown("<h1 class='main-header'>分析ダッシュボード</h1>", unsafe_allow_html=True)
    
    # サンプルデータの生成（実際のアプリではAPIから取得）
    def generate_sample_data():
        dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
        data = {
            'date': dates,
            'requests': [random.randint(50, 200) for _ in range(30)],
            'avg_response_time': [random.uniform(0.5, 3.0) for _ in range(30)],
            'success_rate': [random.uniform(0.8, 1.0) for _ in range(30)]
        }
        return pd.DataFrame(data)
    
    df = generate_sample_data()
    
    # メトリクスの表示
    st.markdown("<h2 class='sub-header'>主要メトリクス</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("総リクエスト数", f"{df['requests'].sum():,}")
    with col2:
        st.metric("平均応答時間", f"{df['avg_response_time'].mean():.2f}秒")
    with col3:
        st.metric("成功率", f"{df['success_rate'].mean()*100:.1f}%")
    with col4:
        st.metric("バッチ処理数", f"{len(st.session_state.batch_requests)}")
    
    # タブで分析を分ける
    tab1, tab2, tab3 = st.tabs(["リクエスト分析", "応答時間分析", "成功率分析"])
    
    with tab1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("日別リクエスト数")
        fig = px.line(df, x='date', y='requests', markers=True)
        fig.update_layout(
            xaxis_title="日付",
            yaxis_title="リクエスト数",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("応答時間の推移")
        fig = px.line(df, x='date', y='avg_response_time', markers=True)
        fig.update_layout(
            xaxis_title="日付",
            yaxis_title="平均応答時間（秒）",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("応答時間の分布")
        fig = px.histogram(df, x='avg_response_time', nbins=20)
        fig.update_layout(
            xaxis_title="応答時間（秒）",
            yaxis_title="頻度",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("成功率の推移")
        fig = px.line(df, x='date', y='success_rate', markers=True)
        fig.update_layout(
            xaxis_title="日付",
            yaxis_title="成功率",
            height=400,
            yaxis=dict(tickformat='.0%')
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 円グラフ
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("リクエスト結果の内訳")
        
        success_count = int(df['success_rate'].mean() * df['requests'].sum())
        fail_count = df['requests'].sum() - success_count
        
        fig = go.Figure(data=[go.Pie(
            labels=['成功', '失敗'],
            values=[success_count, fail_count],
            hole=.4,
            marker_colors=['#10B981', '#EF4444']
        )])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# 設定ページ
elif page == "設定":
    st.markdown("<h1 class='main-header'>設定</h1>", unsafe_allow_html=True)
    
    # API設定
    st.markdown("<h2 class='sub-header'>API設定</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    api_url = st.text_input("API URL", value=st.session_state.api_url)
    if st.button("接続テスト"):
        try:
            response = requests.get(f"{api_url}/health", timeout=2)
            if response.status_code == 200:
                st.success("接続成功！")
                st.session_state.api_url = api_url
            else:
                st.error(f"接続エラー: ステータスコード {response.status_code}")
        except Exception as e:
            st.error(f"接続エラー: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 表示設定
    st.markdown("<h2 class='sub-header'>表示設定</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    st.checkbox("ダークモード", value=st.session_state.dark_mode, key="dark_mode_setting")
    if st.session_state.dark_mode != st.session_state.dark_mode_setting:
        st.session_state.dark_mode = st.session_state.dark_mode_setting
        st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # チャット履歴
    st.markdown("<h2 class='sub-header'>チャット履歴</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    if st.button("チャット履歴をクリア"):
        st.session_state.chat_history = []
        st.success("チャット履歴をクリアしました")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # バッチリクエスト履歴
    st.markdown("<h2 class='sub-header'>バッチリクエスト履歴</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    if st.button("バッチリクエスト履歴をクリア"):
        st.session_state.batch_requests = []
        st.success("バッチリクエスト履歴をクリアしました")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # アプリ情報
    st.markdown("<h2 class='sub-header'>アプリ情報</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    st.markdown("""
    **AI Assistant Dashboard**
    
    バージョン: 1.0.0
    
    使用モデル: Mixtral 8x7B
    
    このアプリケーションは、AI言語モデルを使用したテキスト生成のためのインターフェースを提供します。
    チャット機能、バッチ処理、分析ダッシュボードを備えています。
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# フッター
st.markdown("---")
st.caption("AI Assistant Dashboard | 最終更新: 2025年4月30日")
