import streamlit as st
import json
import random
import pandas as pd
import re

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="AI 職安衛智能助理",
    page_icon="👷",
    layout="wide"
)

# --- 2. 資料讀取函式 ---
@st.cache_data
def load_data():
    try:
        with open("osha_rules_enriched.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

data = load_data()

# 將資料轉換成 Pandas DataFrame
if data:
    df = pd.DataFrame(data)
else:
    df = pd.DataFrame()

# --- 3. 側邊欄導航 ---
st.sidebar.title("🛡️ 職安衛戰情中心")
st.sidebar.caption("乙級技術士備考系統 v6.0")

# 修改點 1：在選單最前面加入 "🏠 系統首頁"
page = st.sidebar.radio("功能模組", 
    ["🏠 系統首頁", "📊 戰情儀表板", "🔎 法規智能檢索", "🛠️ 術科計算神器", "🔗 外部資源整合"]
)

# --- 功能零：系統首頁 (NEW!) ---
if page == "🏠 系統首頁":
    # 修改點 2：因為圖片是直式的 (9:16)，直接放會太大
    # 我們用「三欄排版」把圖片夾在中間，模擬手機介面的感覺，這樣最美
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        try:
            # 顯示圖片 (use_container_width=True 會讓圖片自動適應欄位寬度)
            st.image("cover.png", use_container_width=True)
            
            # 加一個帥氣的開始按鈕 (裝飾用，增加儀式感)
            st.button("🚀 點擊左側選單，開始你的特訓！", type="primary", use_container_width=True)
            
        except FileNotFoundError:
            st.error("⚠️ 找不到封面圖！請確認檔名是否為 cover.png 且放在同目錄下。")

# --- 功能一：儀表板 ---
elif page == "📊 戰情儀表板":
    st.title("📊 職安衛大數據分析")
    # ... (下面維持原本的程式碼，不用動)
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔥 歷年常考危害熱點")
            all_tags = [t for tags in df["tags"] for t in tags]
            st.bar_chart(pd.Series(all_tags).value_counts())
        with col2:
            st.subheader("💡 備考策略建議")
            st.success("根據分析，**「高處作業」** 與 **「化學危害」** 佔比最高。")
            st.info("含數字的法規共有 **86** 條，建議優先背誦。")
            st.metric("法規資料庫總量", f"{len(df)} 條", delta="已更新至最新")

# --- 功能二：檢索 + 抽卡 ---
elif page == "🔎 法規智能檢索":
    st.title("🔎 法規智能檢索系統")
    tab1, tab2 = st.tabs(["關鍵字搜尋", "⚡ 隨機抽題 (Flashcards)"])
    
    with tab1:
        query = st.text_input("請輸入關鍵字", placeholder="輸入：合梯、缺氧、護欄...")
        if query:
            results = [d for d in data if query in d["content"]]
            st.write(f"搜尋結果：{len(results)} 筆")
            for item in results:
                with st.expander(f"{item['article_no']}"):
                    st.markdown(item['content'].replace(query, f"**[:red[{query}]]**"))
                    if item.get("key_numbers"):
                        st.caption(f"🔢 考點：{', '.join(item['key_numbers'])}")

    with tab2:
        st.write("利用零碎時間，隨機複習含數字法規。")
        if st.button("🎲 隨機抽一題"):
            nums = [d for d in data if "含數字" in d.get("tags", [])]
            if nums:
                q = random.choice(nums)
                st.session_state.flashcard = q
    
        if 'flashcard' in st.session_state:
            q = st.session_state.flashcard
            txt = q['content']
            for n in q.get('key_numbers', []):
                txt = txt.replace(n, " **[_______]** ")
            st.info(f"### {q['article_no']}\n\n{txt}")
            if st.button("👀 看答案"):
                st.success(q['content'])
                st.warning(f"記憶重點：{', '.join(q['key_numbers'])}")

# --- 功能三：術科計算 ---
elif page == "🛠️ 術科計算神器":
    st.title("🛠️ 術科計算神器")
    type_ = st.selectbox("選擇題型", ["時量平均濃度 (TWA)", "失能傷害頻率 (FR)"])
    
    if type_ == "時量平均濃度 (TWA)":
        with st.form("twa"):
            st.info("公式：TWA = Σ(C × T) / 8")
            c1=st.number_input("C1",0.0); t1=st.number_input("T1",0.0)
            c2=st.number_input("C2",0.0); t2=st.number_input("T2",0.0)
            pel=st.number_input("PEL (容許濃度)", 100.0)
            if st.form_submit_button("🚀 計算並判定"):
                twa = (c1*t1 + c2*t2)/8
                st.latex(r"TWA = \frac{C_1 T_1 + C_2 T_2}{8}")
                st.code(f"計算過程：\n({c1}*{t1} + {c2}*{t2}) / 8 = {twa:.2f}")
                if twa > pel: st.error(f"❌ {twa:.2f} > {pel} (不合格)")
                else: st.success(f"✅ {twa:.2f} < {pel} (合格)")
    
    elif type_ == "失能傷害頻率 (FR)":
        with st.form("fr"):
            st.info("公式：FR = (N × 1,000,000) / H")
            n=st.number_input("失能人次",0); h=st.number_input("總工時",0)
            if st.form_submit_button("🚀 計算"):
                if h>0:
                    fr = (n*1000000)/h
                    st.latex(r"FR = \frac{N \times 10^6}{H}")
                    st.success(f"FR = {fr:.2f}")

# --- 功能四：外部資源 ---
elif page == "🔗 外部資源整合":
    st.title("🔗 備考資源中控台")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 NotebookLM 知識庫")
        st.write("利用 Google Gemini 模型進行 AI 考古題問答。")
        st.link_button("👉 前往 NotebookLM", "https://notebooklm.google.com/")
    with col2:
        st.subheader("📝 阿摩線上測驗")
        st.write("全國最大題庫平台，進行大量刷題。")
        st.link_button("👉 前往阿摩 (Yamol)", "https://yamol.tw/")