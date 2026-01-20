import sqlite3
import json
import os

DB_NAME = "osha_app.db"

# --- 1. 精選學科試題資料 (這裡只放選擇題，術科我們用 add_subjective.py 加) ---
questions_data = [
    # ... (為了版面整潔，這裡只保留一題範例，反正這支程式主要目的是建立新架構) ...
    # 實際執行時，我們會用 add_subjective.py 把術科灌進去
    {
        "id": 101, "category": "法規與管理", "question": "依職業安全衛生教育訓練規則規定，教育訓練相關紀錄應保存幾年？",
        "options": ["1年", "2年", "3年", "4年"], "answer": "3年",
        "explanation": "依規應保存 3 年。(108年學科)", "mnemonic": "", "keywords": [], "hint": ""
    }
]

def init_database():
    # 強制刪除舊資料庫，建立新的架構
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print("🗑️ 舊資料庫已移除 (為了升級架構)")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. 建立「題目表」 (新增 keywords 和 hint 欄位)
    c.execute('''
        CREATE TABLE questions (
            id INTEGER PRIMARY KEY,
            category TEXT,
            type TEXT,
            question TEXT,
            options TEXT,
            answer TEXT,
            explanation TEXT,
            mnemonic TEXT,
            keywords TEXT,
            hint TEXT
        )
    ''')

    # 2. 建立「錯題紀錄表」
    c.execute('''
        CREATE TABLE error_log (
            user_id TEXT,
            question_id INTEGER,
            PRIMARY KEY (user_id, question_id)
        )
    ''')

    print("✅ V12.0 資料表架構建立完成 (含 AI 引導欄位)")

    # 寫入範例題
    for q in questions_data:
        options_str = json.dumps(q["options"], ensure_ascii=False)
        keywords_str = json.dumps(q["keywords"], ensure_ascii=False)
        
        c.execute('''
            INSERT INTO questions (id, category, type, question, options, answer, explanation, mnemonic, keywords, hint)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (q["id"], q["category"], "choice", q["question"], options_str, q["answer"], q["explanation"], q["mnemonic"], keywords_str, q["hint"]))

    conn.commit()
    conn.close()
    print("🎉 資料庫重置成功！請接著執行 add_subjective.py 注入術科題。")

if __name__ == "__main__":
    init_database()