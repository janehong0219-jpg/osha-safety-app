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

db.init_db()

# --- 🎨 UI 優化 ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif; }
    [data-testid="stSidebar"] { background-color: #0f172a; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stButton > button { border-radius: 12px; font-weight: bold; }
    
    /* AI 對話框樣式 */
    .ai-chat-box {
        background-color: #f0f9ff;
        border-left: 5px solid #0ea5e9;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        color: #333;
    }
    .user-input-area textarea {
        background-color: #fff;
        border: 2px solid #cbd5e1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料讀取 ---
def load_exam_questions():
    # 這裡要稍微修改 db.py 的讀取邏輯來支援 keyword，但為了方便，我們直接在 app.py 處理
    # 為了簡化，我們直接讀取資料庫，並手動解析 JSON 欄位
    conn = db.sqlite3.connect(db.DB_NAME)
    conn.row_factory = db.sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM questions")
    rows = c.fetchall()
    questions = []
    for row in rows:
        q = dict(row)
        q['options'] = json.loads(q['options'])
        # 嘗試解析 keywords (如果是舊資料可能沒有這個欄位，要做防呆)
        try:
            q['keywords'] = json.loads(q['keywords']) if q['keywords'] else []
        except:
            q['keywords'] = []
        questions.append(q)
    conn.close()
    return questions

all_questions = load_exam_questions()
current_error_ids = db.get_error_ids()

# 資料分流
choice_questions = [q for q in all_questions if q.get('type') == 'choice']
essay_questions = [q for q in all_questions if q.get('type') == 'essay']

# --- 3. 側邊欄 ---
st.sidebar.title("🛡️ 職安衛戰情中心")
st.sidebar.caption("v12.0 術科特訓版")

error_count = len(current_error_ids)
error_label = f"📕 我的錯題本 ({error_count})" if error_count > 0 else "📕 我的錯題本"

page = st.sidebar.radio("學習路徑", 
    ["🏠 系統首頁", "🔥 術科特訓班", "📚 主題觀念特訓", "📝 歷屆試題演練", error_label, "📊 戰情儀表板", "⚡ 必背數字神表"]
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
            st.button("🚀 開始特訓！", type="primary", use_container_width=True)
        except: st.warning("請上傳 cover.png")

# --- 🔥 術科特訓班 (核心新功能) ---
elif page == "🔥 術科特訓班":
    st.title("🔥 術科 AI 特訓班")
    st.info("這裡不是單純的背答案，而是由 **AI 導師** 一步步引導你寫出申論題關鍵字。")
    
    if not essay_questions:
        st.warning("目前題庫中沒有術科題，請執行 add_subjective.py")
    else:
        # 選擇題目
        q_options = [f"Q{q['id']}: {q['question'][:20]}..." for q in essay_questions]
        selected_q_str = st.selectbox("請選擇要練習的題目：", q_options)
        
        # 找出選到的題目完整資料
        q_idx = q_options.index(selected_q_str)
        q = essay_questions[q_idx]
        
        st.markdown("---")
        
        # 步驟 1: 顯示題目
        st.subheader(f"📝 題目：")
        st.markdown(f"### {q['question']}")
        
        # 互動區域
        st.markdown("### ✍️ 你的擬答：")
        user_input = st.text_area("試著寫出你想到的答案 (關鍵字即可)：", height=150, key=f"essay_input_{q['id']}")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        # 按鈕狀態管理
        if 'show_hint' not in st.session_state: st.session_state.show_hint = False
        if 'show_answer' not in st.session_state: st.session_state.show_answer = False
        
        with col1:
            if st.button("💡 給我一點提示"):
                st.session_state.show_hint = True
        
        with col2:
            check_btn = st.button("🤖 AI 批改我的答案", type="primary")

        with col3:
             if st.button("👀 直接看完整解答"):
                 st.session_state.show_answer = True
        
        # 邏輯回饋區
        if st.session_state.show_hint:
            st.markdown(f"""
            <div class="ai-chat-box">
                <b>🤖 AI 導師提示：</b><br>
                {q.get('hint', '這題沒有提示，請直接回想關鍵字！')}
            </div>
            """, unsafe_allow_html=True)
            
        if check_btn:
            if not user_input:
                st.warning("請先輸入你的答案，AI 才能幫你批改喔！")
            else:
                # 簡單的關鍵字比對邏輯
                score = 0
                hit_keywords = []
                missed_keywords = []
                
                keywords = q.get('keywords', [])
                for kw in keywords:
                    if kw in user_input:
                        score += 1
                        hit_keywords.append(kw)
                    else:
                        missed_keywords.append(kw)
                
                # 顯示批改結果
                if score == len(keywords):
                    st.balloons()
                    st.success(f"🎉 太神了！你命中了所有關鍵字：{hit_keywords}")
                elif score > 0:
                    st.info(f"👍 不錯喔！你寫出了：{hit_keywords}")
                    st.error(f"⚠️ 但是漏掉了這些關鍵字：{missed_keywords}")
                    st.markdown("**建議：再試著把漏掉的詞加進去句子裡！**")
                else:
                    st.error("😫 哎呀，AI 找不到任何關鍵字。試著按「給我一點提示」看看？")

        if st.session_state.show_answer:
            st.markdown("---")
            st.markdown(f"""
            <div style="background-color:#ecfdf5; padding:20px; border-radius:10px; border:2px solid #10b981;">
                <h3 style="color:#047857; margin-top:0;">✅ 標準解答</h3>
                <pre style="white-space: pre-wrap; font-size:18px;">{q['answer']}</pre>
                <hr>
                <p><b>🔑 {q.get('mnemonic', '')}</b></p>
                <p style="color:#666;">{q['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)


# --- 📚 主題觀念特訓 ---
elif page == "📚 主題觀念特訓":
    st.title("📚 主題觀念特訓")
    categories = list(set([q.get('category', '未分類') for q in choice_questions if "考古題" not in q.get('category', '')]))
    if not categories: st.info("目前無資料")
    else:
        selected_cat = st.selectbox("章節", categories)
        filtered_q = [q for q in choice_questions if q.get('category') == selected_cat]
        for q in filtered_q:
            with st.expander(f"Q{q['id']}: {q['question']}"):
                if st.radio("選項", q['options'], key=f"c_{q['id']}") == q['answer']: st.success("✅ 答對")
                else: st.error(f"❌ 答錯，答案：{q['answer']}")

# --- 📝 歷屆試題演練 ---
elif page == "📝 歷屆試題演練":
    st.title("📝 歷屆試題演練")
    exam_categories = list(set([q.get('category', '未分類') for q in choice_questions if "考古題" in q.get('category', '')]))
    if not exam_categories: st.warning("無考古題資料")
    else:
        exam_categories.sort(reverse=True)
        selected_exam = st.selectbox("屆次", exam_categories)
        filtered_q = [q for q in choice_questions if q.get('category') == selected_exam]
        for q in filtered_q:
            with st.expander(f"Q{q['id']}: {q['question']}"):
                if st.radio("選項", q['options'], key=f"e_{q['id']}") == q['answer']: st.success("✅ 答對")
                else: st.error(f"❌ 答錯，答案：{q['answer']}")

# --- 📕 我的錯題本 ---
elif "📕 我的錯題本" in page:
    st.title("📕 我的錯題本")
    current_error_ids = db.get_error_ids()
    if not current_error_ids: st.success("無錯題！")
    else:
        error_qs = [q for q in choice_questions if q['id'] in current_error_ids]
        for q in error_qs:
            st.markdown(f"**Q{q['id']}: {q['question']}**")
            if st.radio("重做", q['options'], key=f"err_{q['id']}") == q['answer']:
                st.success("✅ 答對")
                if st.button(f"移除 Q{q['id']}", key=f"rm_{q['id']}"):
                    db.remove_error(q['id']); st.rerun()
            else: st.error("❌ 錯")
            st.markdown("---")
# --- 其他功能保留 ---
elif page == "📊 戰情儀表板":
    st.title("📊 戰情儀表板"); st.metric("總題數", len(all_questions))
elif page == "⚡ 必背數字神表":
    st.title("⚡ 必背數字神表")
    st.dataframe(pd.DataFrame({"項目": ["護欄高度", "缺氧濃度"], "數字": ["90cm", "18%"]}), use_container_width=True)