import streamlit as st
import json
import random
import pandas as pd
import os
import time
import db  # 匯入資料庫模組

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="AI 職安衛戰情中心",
    page_icon="🛡️",
    layout="wide"
)

# --- 初始化資料庫 ---
db.init_db()

# --- 🎨 UI 優化 (CSS 強制配色版) ---
st.markdown("""
    <style>
    /* 全域字體設定 */
    html, body, [class*="css"] { 
        font-family: "Microsoft JhengHei", sans-serif; 
    }

    /* --- 側邊欄專屬設定 (深色戰情風) --- */
    [data-testid="stSidebar"] { 
        background-color: #0f172a; /* 深藍黑色背景 */
    }
    
    /* 側邊欄的所有文字強制變白 */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* 側邊欄選單按鈕優化 */
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
        font-size: 18px !important;
        padding: 10px;
        border-radius: 8px;
        transition: background 0.3s;
    }
    
    /* 滑鼠移過去變亮一點 */
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: #1e293b; 
    }

    /* --- 主畫面按鈕與樣式 --- */
    .stButton > button {
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        font-size: 18px !important; 
        font-weight: bold;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1); 
        transition: all 0.3s ease;
    }
    .stButton > button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0px 5px 10px rgba(0,0,0,0.2); 
    }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { 
        font-size: 18px; 
        border-radius: 8px; 
    }
    
    h1 { 
        color: #1E3A8A; 
        border-bottom: 3px solid #E5E7EB; 
        padding-bottom: 10px; 
    }
    
    /* 錯題本卡片特效 */
    .error-card { 
        border-left: 5px solid #ef4444; 
        background-color: #fef2f2; 
        padding: 15px; 
        border-radius: 5px; 
        margin-bottom: 10px; 
        color: #000000; /* 卡片內文字強制黑色 */
    }
    
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
        color: #000000; /* 卡片內文字強制黑色 */
    }
    .flashcard:hover { border-color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料讀取 ---
@st.cache_data
def load_data():
    try:
        with open("osha_rules_enriched.json", "r", encoding="utf-8") as f: return json.load(f)
    except: return []

@st.cache_data
def load_exam_questions():
    try:
        with open("exam_questions.json", "r", encoding="utf-8") as f: return json.load(f)
    except: return []

data = load_data()
all_questions = load_exam_questions()
current_error_ids = db.get_error_ids()

choice_questions = [q for q in all_questions if q.get('type') == 'choice']
essay_questions = [q for q in all_questions if q.get('type') == 'essay']
df = pd.DataFrame(data) if data else pd.DataFrame()

# --- 3. 側邊欄 ---
st.sidebar.title("🛡️ 職安衛戰情中心")
st.sidebar.caption("v10.2 戰情黑化版")

error_count = len(current_error_ids)
error_label = f"📕 我的錯題本 ({error_count})" if error_count > 0 else "📕 我的錯題本"

page = st.sidebar.radio("學習路徑", 
    ["🏠 系統首頁", "📚 章節系統學習", error_label, "🧠 術科關鍵字翻牌", "📊 戰情儀表板", "⚡ 必背數字神表", "🛠️ 術科計算神器", "🔎 法規智能檢索"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 推薦備考資源")
c1, c2 = st.sidebar.columns(2)
with c1: st.link_button("📖 必買題庫", "https://www.books.com.tw/") 
with c2: st.link_button("⛑️ 工安安全鞋", "https://shopee.tw/")

# --- 功能區塊 ---

if page == "🏠 系統首頁":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("cover.png", use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("🚀 開始特訓！", type="primary", use_container_width=True)
        except: st.warning("請上傳 cover.png")

elif page == "📚 章節系統學習":
    st.title("📚 章節系統學習")
    
    categories = list(set([q.get('category', '未分類') for q in choice_questions]))
    selected_cat = st.selectbox("請選擇章節主題：", categories)
    filtered_q = [q for q in choice_questions if q.get('category') == selected_cat]
    
    if not filtered_q:
        st.info("本章節尚無題目。")
    else:
        st.success(f"【{selected_cat}】章節共有 {len(filtered_q)} 題")
        
        for i, q in enumerate(filtered_q):
            is_in_error_log = q['id'] in current_error_ids
            title_prefix = "❌ [需複習] " if is_in_error_log else ""
            
            with st.expander(f"{title_prefix}Q{q['id']}: {q['question']}"):
                user_ans = st.radio("選項", q['options'], key=f"cat_{q['id']}", index=None)
                
                if user_ans:
                    if user_ans == q['answer']:
                        st.success("✅ **答對！**")
                        if is_in_error_log:
                            db.remove_error(q['id'])
                            st.toast(f"已將 Q{q['id']} 從錯題本移除！", icon="🎉")
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.error(f"❌ **答錯**，答案是：{q['answer']}")
                        if not is_in_error_log:
                            db.add_error(q['id'])
                            st.toast(f"已將 Q{q['id']} 加入錯題本！", icon="📝")
                            time.sleep(0.5)
                            st.rerun()

                        if "mnemonic" in q: st.warning(f"🔑 **獨家記憶法：** {q['mnemonic']}")

                        col_ai_1, col_ai_2 = st.columns([1, 3])
                        with col_ai_1:
                             if st.button(f"🤖 呼叫 AI 老師", key=f"ai_{q['id']}"):
                                with st.spinner("AI 老師正在思考..."):
                                    time.sleep(1)
                                    st.info(f"🎓 **AI 解析：**\n\n{q['explanation']}\n\n同學加油，這題是必考題喔！")

elif "📕 我的錯題本" in page:
    st.title("📕 我的錯題本")
    st.markdown("請把這裡清空，你就離考上不遠了！")
    
    current_error_ids = db.get_error_ids()
    
    if not current_error_ids:
        st.balloons()
        st.success("太強了！目前沒有錯題，你是職安衛戰神！🏆")
    else:
        error_qs = [q for q in choice_questions if q['id'] in current_error_ids]
        st.write(f"目前累積錯題：**{len(error_qs)}** 題")
        st.progress(len(error_qs) / len(choice_questions), text="錯題率指標")
        
        for i, q in enumerate(error_qs):
            st.markdown(f"""<div class="error-card"><b>Q{q['id']}: {q['question']}</b></div>""", unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            with col1: user_ans = st.radio("請重新作答：", q['options'], key=f"err_{q['id']}", index=None)
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"✨ 我學會了", key=f"btn_remove_{q['id']}"):
                    db.remove_error(q['id'])
                    st.toast("移除成功！")
                    time.sleep(0.5)
                    st.rerun()

            if user_ans:
                if user_ans == q['answer']: st.success("✅ 答對了！點擊右側按鈕將此題移除。")
                else: 
                    st.error("❌ 還是錯...再想一下！")
                    if "mnemonic" in q: st.warning(f"🔑 口訣：{q['mnemonic']}")
            st.markdown("---")

elif page == "🧠 術科關鍵字翻牌":
    st.title("🧠 術科問答題特訓")
    if not essay_questions: st.warning("題庫中無術科題")
    else:
        if 'essay_idx' not in st.session_state: st.session_state.essay_idx = 0
        if 'is_flipped' not in st.session_state: st.session_state.is_flipped = False
        if st.session_state.essay_idx >= len(essay_questions): st.session_state.essay_idx = 0
        q = essay_questions[st.session_state.essay_idx]
        
        st.progress((st.session_state.essay_idx + 1) / len(essay_questions), text=f"第 {st.session_state.essay_idx + 1}/{len(essay_questions)} 題")
        
        if st.session_state.is_flipped:
            st.markdown(f"""<div class="flashcard" style="background-color:#f0fdf4; border-color:#22c55e;"><div style="font-size:24px;font-weight:bold;">✅ 參考解答</div><div style="font-size:20px;white-space:pre-line;">{q['answer']}</div><hr><div style="color:#888;">{q['explanation']}</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="flashcard"><div style="font-size:24px;font-weight:bold;">❓ 題目</div><div style="font-size:20px;">{q['question']}</div><div style="color:#aaa;margin-top:20px;">(點擊下方按鈕翻牌)</div></div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 2, 1])
        if c1.button("⬅️ 上一題"): 
            st.session_state.essay_idx = max(0, st.session_state.essay_idx - 1); st.session_state.is_flipped = False; st.rerun()
        btn_txt = "🫣 遮住" if st.session_state.is_flipped else "👀 看答案"
        if c2.button(btn_txt, type="primary"): 
            st.session_state.is_flipped = not st.session_state.is_flipped; st.rerun()
        if c3.button("下一題 ➡️"): 
            st.session_state.essay_idx = min(len(essay_questions) - 1, st.session_state.essay_idx + 1); st.session_state.is_flipped = False; st.rerun()

elif page == "📊 戰情儀表板":
    st.title("📊 職安衛大數據分析")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: st.subheader("🔥 危害熱點"); all_tags = [t for tags in df["tags"] for t in tags]; st.bar_chart(pd.Series(all_tags).value_counts())
        with c2: 
            st.subheader("💡 學習狀況")
            st.metric("總題數", f"{len(choice_questions)} 題")
            st.metric("待複習錯題", f"{len(current_error_ids)} 題", delta="需加油" if current_error_ids else "完美", delta_color="inverse")

elif page == "⚡ 必背數字神表":
    st.title("⚡ 職安衛關鍵數字速查")
    df_cheat = pd.DataFrame({"類別": ["教育訓練", "設施標準", "勞基法補償", "設施標準", "設施標準", "健康保護", "化學品", "營造標準"], "項目": ["訓練紀錄保存", "護欄高度", "職災死亡補償", "固定梯平台間距", "餐廳人均面積", "急救人員比例", "GHS標示容器", "屋頂作業斜度"], "關鍵數字": ["3 年", "90 公分以上", "45 個月 (5+40)", "9 公尺", "1 平方公尺", "每 50 人置 1 人", "100 毫升以下", "34 度"]})
    filter_txt = st.text_input("🔍 搜尋", "")
    if filter_txt: df_cheat = df_cheat[df_cheat.apply(lambda row: row.astype(str).str.contains(filter_txt).any(), axis=1)]
    st.dataframe(df_cheat, use_container_width=True, hide_index=True)

elif page == "🛠️ 術科計算神器":
    st.title("🛠️ 術科計算神器")
    type_ = st.selectbox("題型", ["時量平均濃度 (TWA)", "失能傷害頻率 (FR)"])
    st.markdown("<br>", unsafe_allow_html=True)
    if type_ == "時量平均濃度 (TWA)":
        with st.form("twa"):
            st.info("公式：TWA = Σ(C × T) / 8")
            c1, c2 = st.columns(2)
            with c1: v1=st.number_input("C1",0.0); t1=st.number_input("T1",0.0); v2=st.number_input("C2",0.0); t2=st.number_input("T2",0.0)
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

elif page == "🔎 法規智能檢索":
    st.title("🔎 法規智能檢索")
    query = st.text_input("輸入關鍵字", placeholder="合梯...")
    if query:
        results = [d for d in data if query in d["content"]]
        st.success(f"找到 {len(results)} 筆")
        for item in results:
            with st.expander(f"{item['article_no']}"): st.markdown(item['content'].replace(query, f"**[:red[{query}]]**"))