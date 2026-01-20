import pdfplumber
import sqlite3
import re
import os
import json
import glob

# 設定資料庫名稱
DB_NAME = "osha_app.db"

def extract_questions_from_pdf(pdf_path):
    print(f"📄 正在處理檔案：{os.path.basename(pdf_path)} ...")
    questions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        # 讀取每一頁的文字
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    # --- 核心邏輯：文字清洗與正規表達式 ---
    
    # 1. 先把換行符號拿掉，避免題目被斷行切開
    # 但為了保持題目間的區隔，我們先用一個特殊符號標記題目開頭
    # 勞動部題型特徵： "數字. ( 答案 )" 或 "數字. (答案)"
    # Regex: 抓取 "1. ( 3 )" 這種格式
    
    # 將文字中的換行取代為空格，方便 regex 抓取整段
    clean_text = full_text.replace('\n', '')
    
    # 定義 Regex 模式 (針對勞動部 PDF 格式)
    # 群組1: 題號, 群組2: 答案, 群組3: 題目內容(含選項)
    # 支援全形括號（）和半形括號()
    pattern = r"(\d+)\.\s*[（\(]\s*([1-4])\s*[）\)]\s*(.*?)(?=\d+\.\s*[（\(]|$)"
    
    matches = re.findall(pattern, clean_text)
    
    if not matches:
        print(f"⚠️  警告：在 {os.path.basename(pdf_path)} 中找不到符合格式的題目。可能格式不同。")
        return []

    year_name = os.path.basename(pdf_path).split('.')[0] # 用檔名當作分類參考

    for match in matches:
        q_id_raw = match[0]
        ans = match[1]
        content_raw = match[2].strip()
        
        # --- 嘗試分離選項 ①②③④ ---
        # 勞動部的選項通常用 ①②③④ 或 1. 2. 3. 4.
        # 這裡做一個簡單的切割嘗試
        options = []
        question_text = content_raw
        
        # 嘗試用圓圈數字切割
        if '①' in content_raw:
            parts = re.split(r'[①②③④]', content_raw)
            if len(parts) >= 5: # 題目 + 4個選項
                question_text = parts[0].strip()
                options = [p.strip() for p in parts[1:5]]
            else:
                # 切割失敗，保留原文
                options = ["(詳見題目)", "(詳見題目)", "(詳見題目)", "(詳見題目)"]
        else:
             options = ["(詳見題目)", "(詳見題目)", "(詳見題目)", "(詳見題目)"]

        # 整理一題的資料
        q_data = {
            # 為了避免不同年份題號重複(都是第1題)，我們用 "年份-題號" 當作暫時 ID，或是讓資料庫自動跳號
            # 這裡我們只回傳資料，讓存入函式處理 ID
            "original_id": q_id_raw, 
            "category": f"{year_name} 考古題", # 自動分類
            "question": question_text,
            "options": options,
            "answer": map_answer_to_option(ans, options), # 嘗試把 "3" 轉成選項內容
            "explanation": f"出處：{year_name} 第 {q_id_raw} 題"
        }
        questions.append(q_data)
        
    print(f"✅ 成功提取 {len(questions)} 題")
    return questions

def map_answer_to_option(ans_index, options):
    """將答案索引 (1,2,3,4) 轉成文字，如果選項解析失敗則回傳 '第x選項'"""
    try:
        idx = int(ans_index) - 1
        if 0 <= idx < len(options) and options[0] != "(詳見題目)":
            return options[idx]
        else:
            return f"答案：選項 {ans_index}"
    except:
        return f"答案：{ans_index}"

def save_to_db(all_questions):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 取得目前資料庫最大的 ID，以便接著編號
    c.execute("SELECT MAX(id) FROM questions")
    max_id = c.fetchone()[0]
    if max_id is None:
        max_id = 0
    
    current_id = max_id + 1
    count = 0
    
    print("💾 正在寫入資料庫...")
    
    for q in all_questions:
        # 檢查是否題目內容已存在 (避免重複匯入)
        c.execute("SELECT id FROM questions WHERE question = ?", (q['question'],))
        exists = c.fetchone()
        
        if not exists:
            options_str = json.dumps(q["options"], ensure_ascii=False)
            
            c.execute('''
                INSERT INTO questions (id, category, type, question, options, answer, explanation, mnemonic)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                current_id, 
                q["category"], 
                "choice", 
                q["question"], 
                options_str, 
                q["answer"], 
                q["explanation"], 
                "" # 批量匯入暫無口訣
            ))
            current_id += 1
            count += 1
    
    conn.commit()
    conn.close()
    print(f"🎉 匯入完成！共新增 {count} 題。現在資料庫總題數：{current_id - 1}")

def main():
    # 1. 搜尋資料夾內所有的 PDF 檔案
    pdf_files = glob.glob("*.pdf")
    
    if not pdf_files:
        print("❌ 找不到 PDF 檔案！請確認你已經把 105-108 年的 PDF 放在這個資料夾裡。")
        return

    all_extracted_questions = []
    
    # 2. 迴圈處理每一個 PDF
    for pdf_file in pdf_files:
        qs = extract_questions_from_pdf(pdf_file)
        all_extracted_questions.extend(qs)
        
    # 3. 存入資料庫
    if all_extracted_questions:
        save_to_db(all_extracted_questions)
    else:
        print("⚠️ 沒有抓到任何題目，請檢查 PDF 內容是否為圖片掃描檔 (這支程式只能讀文字檔 PDF)。")

if __name__ == "__main__":
    main()