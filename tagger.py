import json
import re

# 定義關鍵字地圖 (已加入「合梯」、「梯」)
KEYWORDS_MAP = {
    "高處作業": ["高度", "高處", "墜落", "架", "護欄", "安全帶", "合梯", "梯"], 
    "缺氧危險": ["缺氧", "氧氣", "通風", "空氣"],
    "電氣安全": ["電壓", "伏特", "接地", "觸電", "絕緣"],
    "化學危害": ["有機溶劑", "化學", "中毒", "氣體", "粉塵"],
    "高溫/火災": ["高溫", "火災", "爆炸", "易燃"],
    "防護具": ["防護具", "安全帽", "耳塞", "手套"]
}

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"📖 讀取資料庫成功，共 {len(data)} 條")
            return data
    except FileNotFoundError:
        print("❌ 找不到檔案！請先確認 osha_rules.json 存在")
        return []

def analyze_laws(data):
    enriched_data = []
    # 初始化統計字典
    stats = {key: 0 for key in KEYWORDS_MAP.keys()}
    stats["含數字條文"] = 0

    print("🔍 開始分析考點...")

    # 數字偵測正則表達式 (包含 75度)
    pattern = r'([0-9一二三四五六七八九十百千]+[．\.]?[0-9一二三四五六七八九十]*\s*(?:公尺|公分|公厘|伏特|度|小時|日|年|公斤|人|%|倍|℃))'

    for law in data:
        content = law["content"]
        tags = []
        
        # A. 關鍵字標記
        for category, keywords in KEYWORDS_MAP.items():
            if any(k in content for k in keywords):
                tags.append(category)
        
        # 移除重複標籤
        tags = list(set(tags))

        # 統計標籤數量
        for t in tags:
            if t in stats:
                stats[t] += 1

        # B. 數字偵測
        numbers = re.findall(pattern, content)
        valid_numbers = [n for n in numbers if len(n) > 1]
        
        if len(valid_numbers) > 0:
            tags.append("含數字")
            stats["含數字條文"] += 1

        enriched_law = {
            "article_no": law["article_no"],
            "content": content,
            "tags": tags,
            "key_numbers": valid_numbers
        }
        
        enriched_data.append(enriched_law)

    return enriched_data, stats

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ 資料強化完成！已儲存至 {filename}")

# 這一塊就是程式的「引擎」，如果沒複製到，程式就不會跑！
if __name__ == "__main__":
    raw_data = load_json("osha_rules.json")
    if raw_data:
        new_data, statistics = analyze_laws(raw_data)
        save_json(new_data, "osha_rules_enriched.json")
        
        print("\n📊 最新考點分析：")
        print("-" * 30)
        for category, count in statistics.items():
            print(f"{category}: 共 {count} 條")
        print("-" * 30)