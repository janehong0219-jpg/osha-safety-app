# db.py
import sqlite3
import json

DB_NAME = "osha_app.db"

def init_db():
    """初始化資料庫：建立錯題本表格"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 建立一個簡單的表：user_id (目前固定為 'guest'), question_id
    c.execute('''CREATE TABLE IF NOT EXISTS error_log
                 (user_id TEXT, question_id INTEGER, 
                 PRIMARY KEY (user_id, question_id))''')
    conn.commit()
    conn.close()

def add_error(q_id, user_id="guest"):
    """新增錯題"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO error_log VALUES (?, ?)", (user_id, q_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # 已經存在，不用重複加
    conn.close()

def remove_error(q_id, user_id="guest"):
    """移除錯題"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM error_log WHERE user_id=? AND question_id=?", (user_id, q_id))
    conn.commit()
    conn.close()

def get_error_ids(user_id="guest"):
    """取得所有錯題 ID"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT question_id FROM error_log WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]