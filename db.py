import sqlite3
import json
import os

DB_NAME = "osha_app.db"

def init_db():
    """
    確認資料庫是否存在。
    注意：建立資料庫的工作現在交給 setup_database.py 了。
    這裡只做簡單的檢查。
    """
    if not os.path.exists(DB_NAME):
        print("⚠️ 警告：找不到資料庫！請先執行 python setup_database.py")

# --- 錯題本相關功能 ---
def add_error(q_id, user_id="guest"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO error_log VALUES (?, ?)", (user_id, q_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass 
    conn.close()

def remove_error(q_id, user_id="guest"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM error_log WHERE user_id=? AND question_id=?", (user_id, q_id))
    conn.commit()
    conn.close()

def get_error_ids(user_id="guest"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 這裡要加一個 try-except，以免資料庫還沒建立時報錯
    try:
        c.execute("SELECT question_id FROM error_log WHERE user_id=?", (user_id,))
        rows = c.fetchall()
        return [row[0] for row in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()

# --- 題目讀取功能 (NEW!) ---
def get_all_questions():
    """從資料庫讀取所有題目，並轉回字典格式"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # 讓回傳結果可以用欄位名稱存取
    c = conn.cursor()
    
    questions = []
    try:
        c.execute("SELECT * FROM questions")
        rows = c.fetchall()
        
        for row in rows:
            q = dict(row)
            # 把 JSON 字串的 options 轉回 Python List
            q['options'] = json.loads(q['options'])
            questions.append(q)
            
    except sqlite3.OperationalError:
        print("⚠️ 無法讀取題目，請確認資料庫是否已建立")
        
    conn.close()
    return questions