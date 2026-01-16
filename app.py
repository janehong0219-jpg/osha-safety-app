import streamlit as st
import json
import random
import pandas as pd

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="AI 職安衛戰情中心",
    page_icon="🛡️",
    layout="wide"
)

# --- 🎨 UI 優化 (CSS) ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif; }
    [data-testid="stSidebar"] { background-color: #f0f2f6; }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3.5em; font-size: 18px !important; font-weight: bold;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1); transition: all 0.3s ease;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0px 5px 10px rgba(0,0,0,0.2); }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { font-size: 18px; border-radius: 8px; }
    h1 { color: #1E3A8A; border-bottom: 3px solid #E5E7EB; padding-bottom: 10px; }
    
    /* 翻牌卡樣式 */
    .flashcard {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        cursor: pointer;
        margin-bottom: 20px;
    }
    .flashcard:hover { border-color: #1E3A8A; }
    .card-title { font-size: 24px; font-weight: bold; color: #1f2937; margin-bottom: 15px; }
    .card-content { font-size: 20px; color: #4b5563; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料讀取 ---
@st.cache_data
def load_data():
    try:
        with open("osha_rules_enriched.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@st.cache_data
def load_exam_questions():
    try:
        with open("exam_questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

data = load_data()
all_questions = load_exam_questions()

# 資料分流
choice_questions = [q for q in all_questions if q.get('type') == 'choice']
essay_questions = [q for q in all_questions if q.get('type') == 'essay']

# 轉換法規為 DataFrame
df = pd.DataFrame(data) if data else pd.DataFrame()

# --- 3. 側邊欄 ---
st.sidebar.title("🛡️ 職安衛戰情中心")
st.sidebar.caption("v9.0 教科書取代版")

page = st.sidebar.radio("學習路徑", 
    ["🏠 系統首頁", "📚 章節系統學習", "🧠 術科關鍵字翻牌", "📊 戰情儀表板", "⚡ 必背數字神表", "🛠️ 術科計算神器", "🔎 法規智能檢索"]
)

# --- 0. 首頁 ---
if page == "🏠 系統首頁":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("cover.png", use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("🚀 開始特訓！", type="primary", use_container_width=True)
        except: st.warning("請上傳 cover.png")

# --- 1. 章節系統學習 (NEW!) ---
elif page == "📚 章節系統學習":
    st.title("📚 章節系統學習")
    st.markdown("不用翻書，依照章節主題進行針對性刷題。")
    
    # 提取所有分類
    categories = list(set([q.get('category', '未分類') for q in choice_questions]))
    selected_cat = st.selectbox("請選擇章節主題：", categories)
    
    # 篩選題目
    filtered_q = [q for q in choice_questions if q.get('category') == selected_cat]
    
    if not filtered_q:
        st.info("本章節尚無題目。")
    else:
        st.success(f"【{selected_cat}】章節共有 {len(filtered_q)} 題")
        
        # 簡單的循序出題
        for i, q in enumerate(filtered_q):
            with st.expander(f"Q{i+1}: {q['question']}"):
                user_ans = st.radio("選項", q['options'], key=f"cat_{q['id']}")
                if user_ans:
                    if user_ans == q['answer']:
                        st.write("✅ **答對！**")
                    else:
                        st.write(f"❌ **答錯**，答案是：{q['answer']}")
                    st.caption(f"解析：{q['explanation']}")

# --- 2. 術科關鍵字翻牌 (防呆修正版) ---
elif page == "🧠 術科關鍵字翻牌":
    st.title("🧠 術科問答題特訓")
    st.markdown("模擬術科手寫情境，點擊卡片查看關鍵字答案。")
    
    # 【防呆檢查】如果題庫是空的，顯示警告，不要崩潰
    if not essay_questions:
        st.warning("⚠️ 目前題庫中沒有「術科問答題」！請確認 exam_questions.json 是否包含 type='essay' 的資料。")
    else:
        # 只有當題庫有東西時，才執行下面的程式
        if 'essay_idx' not in st.session_state:
            st.session_state.essay_idx = 0
            st.session_state.is_flipped = False

        # 確保索引不會超出範圍 (例如刪除題目後)
        if st.session_state.essay_idx >= len(essay_questions):
             st.session_state.essay_idx = 0

        q = essay_questions[st.session_state.essay_idx]
        
        # 進度
        st.progress((st.session_state.essay_idx + 1) / len(essay_questions), text=f"第 {st.session_state.essay_idx + 1} / {len(essay_questions)} 題")

        # 翻牌區域
        if st.session_state.is_flipped:
            # 背面 (答案)
            st.markdown(f"""
            <div class="flashcard" style="background-color:#f0fdf4; border-color:#22c55e;">
                <div class="card-title">✅ 參考解答</div>
                <div class="card-content" style="white-space: pre-line;">{q['answer']}</div>
                <hr>
                <div style="font-size:16px; color:#888;">{q['explanation']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 正面 (題目)
            st.markdown(f"""
            <div class="flashcard">
                <div class="card-title">❓ 題目</div>
                <div class="card-content">{q['question']}</div>
                <div style="margin-top:20px; font-size:14px; color:#aaa;">(點擊下方按鈕查看答案)</div>
            </div>
            """, unsafe_allow_html=True)

        # 操作按鈕
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("⬅️ 上一題"):
                st.session_state.essay_idx = max(0, st.session_state.essay_idx - 1)
                st.session_state.is_flipped = False
                st.rerun()
        with c2:
            btn_text = "🫣 遮住答案" if st.session_state.is_flipped else "👀 看答案 (翻牌)"
            if st.button(btn_text, type="primary"):
                st.session_state.is_flipped = not st.session_state.is_flipped
                st.rerun()
        with c3:
            if st.button("下一題 ➡️"):
                st.session_state.essay_idx = min(len(essay_questions) - 1, st.session_state.essay_idx + 1)
                st.session_state.is_flipped = False
                st.rerun()

# --- 3. 儀表板 ---
elif page == "📊 戰情儀表板":
    st.title("📊 職安衛大數據分析")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🔥 危害熱點")
            all_tags = [t for tags in df["tags"] for t in tags]
            st.bar_chart(pd.Series(all_tags).value_counts())
        with c2:
            st.subheader("💡 題庫狀態")
            st.metric("法規庫", f"{len(df)} 條")
            st.metric("選擇題", f"{len(choice_questions)} 題")
            st.metric("術科問答", f"{len(essay_questions)} 題")

# --- 4. 必背數字神表 ---
elif page == "⚡ 必背數字神表":
    st.title("⚡ 職安衛關鍵數字速查")
    cheat_data = {
        "類別": ["教育訓練", "設施標準", "勞基法補償", "設施標準", "設施標準", "健康保護", "化學品", "營造標準"],
        "項目": ["訓練紀錄保存", "護欄高度", "職災死亡補償", "固定梯平台間距", "餐廳人均面積", "急救人員比例", "GHS標示容器", "屋頂作業斜度"],
        "關鍵數字": ["3 年", "90 公分以上", "45 個月 (5+40)", "9 公尺", "1 平方公尺", "每 50 人置 1 人", "100 毫升以下", "34 度"]
    }
    df_cheat = pd.DataFrame(cheat_data)
    filter_txt = st.text_input("🔍 搜尋 (例：高度)", "")
    if filter_txt:
        df_cheat = df_cheat[df_cheat.apply(lambda row: row.astype(str).str.contains(filter_txt).any(), axis=1)]
    st.dataframe(df_cheat, use_container_width=True, hide_index=True)

# --- 5. 術科計算 ---
elif page == "🛠️ 術科計算神器":
    st.title("🛠️ 術科計算神器")
    type_ = st.selectbox("題型", ["時量平均濃度 (TWA)", "失能傷害頻率 (FR)"])
    st.markdown("<br>", unsafe_allow_html=True)
    if type_ == "時量平均濃度 (TWA)":
        with st.form("twa"):
            st.info("公式：TWA = Σ(C × T) / 8")
            c1, c2 = st.columns(2)
            with c1:
                v1=st.number_input("C1",0.0); t1=st.number_input("T1",0.0)
                v2=st.number_input("C2",0.0); t2=st.number_input("T2",0.0)
            with c2: pel=st.number_input("PEL", 100.0)
            if st.form_submit_button("🚀 計算"):
                twa = (v1*t1 + v2*t2)/8
                st.success(f"TWA = {twa:.2f} ppm")
                if twa > pel: st.error("不合格") 
                else: st.success("合格")
    elif type_ == "失能傷害頻率 (FR)":
        with st.form("fr"):
            st.info("公式：FR = (N × 10^6) / H")
            n=st.number_input("失能人次",0); h=st.number_input("總工時",0)
            if st.form_submit_button("🚀 計算"):
                if h>0: st.success(f"FR = {(n*1000000)/h:.2f}")

# --- 6. 法規檢索 ---
elif page == "🔎 法規智能檢索":
    st.title("🔎 法規智能檢索")
    query = st.text_input("輸入關鍵字", placeholder="合梯、缺氧...")
    if query:
        results = [d for d in data if query in d["content"]]
        st.success(f"找到 {len(results)} 筆")
        for item in results:
            with st.expander(f"{item['article_no']}"):
                st.markdown(item['content'].replace(query, f"**[:red[{query}]]**"))