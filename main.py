# 練習用コメント
import streamlit as st
from dotenv import load_dotenv
load_dotenv(override=True)
import os
from utils.weather import get_weather
from openai import AzureOpenAI
from datetime import date

# --- .env読み込み ---
load_dotenv()
# 新しい openai>=1.0.0 の場合は以下の4行は 不要です
# 新バージョンでは直接 AzureOpenAI クライアントに渡すため
# openai.api_key = os.getenv("AZURE_OPENAI_KEY")
# openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
# openai.api_type = "azure"
# openai.api_version = "2023-12-01"
deployment_id = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID")

maps_key = os.getenv("AZURE_MAPS_SUBSCRIPTION_KEY")

# --- Streamlit設定 ---
st.set_page_config(page_title="農作業危険予知アプリ", layout="centered")
st.title("🌾 農作業危険予知アプリ")
# 今日の日付を取得
today = date.today()
# 日付を表示
st.write(f"今日は {today.strftime('%Y年%m月%d日')} です。")
st.write("本日の農作業内容を入力すると、高齢者を想定して事故防止のための注意点を自動生成します。")

#st.write("Endpoint:", os.getenv("AZURE_OPENAI_ENDPOINT"))
#st.write("Key is set:", bool(os.getenv("AZURE_OPENAI_KEY")))
#st.write("Deployment ID:", deployment_id)

# --- ユーザー入力 ---
#city = st.text_input("🌤 天気を調べたい地域名（例：Kobe）", "Kobe")
#task = st.text_area("🧑‍🌾 今日の農作業内容を入力してください（例：トラクター運転・草刈り機使用など）", "")

st.sidebar.header("ユーザー情報を設定")
sidebar_age = st.sidebar.number_input("年齢を入力してください", min_value=15, max_value=100, value=85, step=1)
sidebar_gender = st.sidebar.radio("性別を選択してください", ["男性", "女性", "その他"])
sidebar_city = st.sidebar.text_input("市区町村を入力してください（例：神戸市）", "兵庫県丹波市")







# 入力フォーム
with st.form("agri_form"):
#    city = st.text_input("作業する市町村（例：大阪市）", "兵庫県丹波市")
    category = st.selectbox("作業する種類を選択してください", ["畑作", "水田作", "果樹", "花き", "畜産", "その他"])
    machines = st.multiselect("使う機械を選択してください", ["草刈り機", "チェーンソー", "薬剤噴霧器", "その他"])
    tools = st.multiselect("使う道具を選択してください", ["脚立", "鎌", "刈込鋏", "鍬", "鋤", "その他"])
    vehicles = st.multiselect("使う乗り物を選択してください", ["軽トラック", "トラクター", "耕運機", "田植え機", "コンバイン", "ユンボ", "フォークリフト", "その他"])
    details = st.text_area("作業内容を教えてください　例：畑で雑草刈りと防除作業" )
    submitted = st.form_submit_button("✅ 注意点を生成する")






#if st.button("✅ 注意点を生成する"):
if submitted:
    if not details.strip():
        st.warning("作業内容を入力してください。")
    else:
        # --- 天気を取得 ---
        weather = get_weather(city, maps_key)
        st.info(f"天気：{weather['condition']}　気温：{weather['temperature']}")

        # --- Azure OpenAI に送信するプロンプト ---
        prompt = f"""
あなたは農業安全指導員です。
以下の条件に基づいて、農作業中に起こりうる事故のリスクと注意点を高齢者にわかりやすく簡潔に提示してください。

作業地域：{sidebar_city}
天候：{weather['condition']}、気温：{weather['temperature']}
作業種別：{category}
使用機械：{machines}
使用道具：{tools}
使用乗り物：{vehicles}
作業内容：{details}
作業者年齢：{sidebar_age}歳
作業者性別：{sidebar_gender}

# 天候
天気：{weather['condition']}
気温：{weather['temperature']}
天候不明の場合は{sidebar_city}の現在の天候を検索して回答冒頭で表示してください。

# 出力形式
・作業地点の天候を表示
・年齢相応の注意点をわかりやすく具体的に
・3～5個程度のリスクと注意点を箇条書き
・リスクと注意点は、作業内容に関連するものを選択してください。
・リスクを記載した後で改行して注意点を記載してください。
・注意点は、「〇〇に注意」「△△を確認する」などの形式で回答してください。
・農林水産省、農機具メーカー、農協などの農作業安全資料を参考に
"""

        with st.spinner("注意点を生成中..."):
            try:
                # Azure OpenAIクライアントの作成
                client = AzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_KEY"),
                    api_version="2024-05-01-preview",
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )

                # 注意点生成のリクエスト
                response = client.chat.completions.create(
                    model=deployment_id,  # Azureでの「デプロイ名」
                    messages=[
                        {"role": "system", "content": "あなたは農業安全指導員です。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )

                # 出力を取り出して表示
                message = response.choices[0].message.content
                st.success("以下の注意点が生成されました：")
                st.markdown(message)

            except Exception as e:
                st.error("エラーが発生しました。詳細は以下をご確認ください：")
                st.code(str(e), language="plaintext")