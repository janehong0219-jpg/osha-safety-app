import streamlit as st
import json

# 設定網頁標題
st.set_page_config(page_title="職安衛法規小幫手", page_icon="👷")

# 讀取資料函式
@st.cache_data
def load_data():
    try:
        # 嘗試讀取加強版資料
        with open("osha_rules_enriched.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("找不到 osha_rules_enriched.json！請確認你有執行過 crawler.py 和 tagger.py")
        return []

data = load_data()

# 側邊欄
st.sidebar.title("👷 職安衛管理員工具")
search_mode = st.sidebar.radio("選擇模式", ["關鍵字搜尋", "考點瀏覽"])

st.title("🛡️ 職業安全衛生設施規則 - 智慧查詢")

if search_mode == "關鍵字搜尋":
    query = st.text_input("請輸入關鍵字 (例如：缺氧、護欄、2公尺)", "")
    if query:
        results = [d for d in data if query in d["content"] or query in d["article_no"]]
        st.success(f"找到 {len(results)} 條相關法規")
        for item in results:
            with st.expander(f"{item['article_no']}"):
                # 簡單的高亮顯示
                st.write(item['content'])
                if item.get("tags"):
                    st.caption(f"考點：{', '.join(item['tags'])}")

elif search_mode == "考點瀏覽":
    # 這裡對應 tagger.py 裡面的分類
    tag_filter = st.selectbox("選擇主題", ["含數字", "高處作業", "缺氧危險", "電氣安全", "化學危害", "高溫/火災"])
    
    # 篩選資料
    filtered_data = [d for d in data if tag_filter in d.get("tags", [])]
    
    st.info(f"【{tag_filter}】相關法規共有 {len(filtered_data)} 條")
    
    for item in filtered_data:
        st.markdown(f"### {item['article_no']}")
        st.write(item['content'])
        # 顯示關鍵數字
        if item.get("key_numbers"):
            st.warning(f"🔢 必背數字：{', '.join(item['key_numbers'])}")
        st.divider()