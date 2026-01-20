import pdfplumber
import re
import json
import os

# --- 設定區：請確認你的 PDF 檔名跟這裡一模一樣 ---
# 如果你的 PDF 叫別的名字，請改這裡，或者把 PDF 改名成這個
pdf_filename = "109-3職業安全衛生管理學科試題.pdf" 
output_json = "new_questions.json"

def parse_exam_pdf(pdf_path):
    questions = []
    current_q = None
    
    if not os.path.exists(pdf_path):
        print(f"❌ 找不到 PDF 檔：{pdf_path}")
        print("請確認 PDF 是否放在同一個資料夾，且檔名完全正確！")
        return []

    print(f"正在讀取 {pdf_path} ...")
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    lines = full_text.split('\n')
    
    for line in lines:
        line = line.strip()
        # 抓取題目開頭 (例如: "1. ( 3 ) ...")
        match = re.match(r"^(\d+)\.\s*\(\s*([^\)]+)\s*\)\s*(.*)", line)
        
        if match:
            if current_q:
                questions.append(current_q)
            
            q_id = int(match.group(1))
            ans = match.group(2).strip()
            content = match.group(3)
            q_type = "choice" if ans.isdigit() else "true_false"
            
            current_q = {
                "id": q_id,
                "category": "歷屆試題自動匯入", # 標記這是自動抓的
                "type": q_type, 
                "question": content,
                "options": ["(詳見題目)", "(詳見題目)", "(詳見題目)", "(詳見題目)"], # 暫時通用的選項
                "answer": ans,
                "explanation": "本題由 Python 自動從 PDF 擷取。"
            }
        elif current_q:
            current_q["question"] += " " + line

    if current_q:
        questions.append(current_q)
        
    return questions

# --- 執行 ---
if __name__ == "__main__":
    data = parse_exam_pdf(pdf_filename)
    if data:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ 成功！已產出 {len(data)} 題，存檔為 {output_json}")
        print("👉 請打開 new_questions.json 檢查內容！")