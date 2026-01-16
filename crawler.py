import requests
from bs4 import BeautifulSoup
import json
import re

# 修改前 (這是母法，只有 61 條)
# URL = "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=N0060001"

# 修改後 (這是設施規則，有 320+ 條)
URL = "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=N0060009"

def fetch_laws():
    print(f"🚀 啟動終極爬蟲，目標：{URL}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=10) # 設定10秒超時
        response.encoding = 'utf-8' 
        
        # 使用 BeautifulSoup 解析
        soup = BeautifulSoup(response.text, 'html.parser')
        
        laws_data = []
        
        # 【策略改變】
        # 直接瞄準所有 class="col-no" 的格子（這些是放條號的地方）
        # 這樣就算網頁排版亂掉，只要有條號，我們就抓得到
        article_numbers = soup.select('.col-no')
        
        print(f"🎯 瞄準到 {len(article_numbers)} 個潛在條文區塊...")

        for art_no_div in article_numbers:
            # 取得條號文字
            no_text = art_no_div.text.strip()
            
            # 過濾掉不是「第 X 條」的東西（例如表頭、章節名稱）
            if not no_text.startswith("第"):
                continue

            # 尋找它的兄弟姊妹：內容區塊 (col-data)
            # find_next_sibling 會找它隔壁的那個 div
            content_div = art_no_div.find_next_sibling('div', class_='col-data')
            
            if content_div:
                content_text = content_div.text.strip()
                # 清洗多餘空白
                content_text = re.sub(r'\s+', ' ', content_text)
                
                laws_data.append({
                    "article_no": no_text,
                    "content": content_text
                })

        return laws_data

    except Exception as e:
        print(f"❌ 發生嚴重錯誤：{e}")
        return []

def save_to_json(data, filename="osha_rules.json"):
    if not data:
        print("⚠️ 抓取失敗，沒有資料可存")
        return

    # 排序一下，確保是從第1條開始（雖然網頁通常是照順序的）
    # 這裡用一個小技巧把 "第 10 條" 轉成數字 10 來排序，避免 "第 10 條" 排在 "第 2 條" 前面
    try:
        data.sort(key=lambda x: int(re.search(r'\d+', x["article_no"]).group()))
    except:
        pass # 如果排序失敗就算了

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ 成功！總共抓到 {len(data)} 條法規")
    print(f"📄 第一條是：{data[0]['article_no']}")
    print(f"📄 最後一條是：{data[-1]['article_no']}") # 印出最後一條，確認是不是第 300 多條

if __name__ == "__main__":
    data = fetch_laws()
    save_to_json(data)