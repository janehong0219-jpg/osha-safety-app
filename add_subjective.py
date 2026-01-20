import sqlite3
import json

DB_NAME = "osha_app.db"

# --- 術科特訓題庫 (含 AI 引導數據) ---
subjective_data = [
    {
        "id": 301,
        "category": "法規與管理",
        "question": "依職業安全衛生法規定，雇主應宣導該法及有關安全衛生規定，使勞工周知。\n請列舉 5 種足使勞工周知之宣導方式。(10 分)",
        "answer": "1. 公告。\n2. 發給印刷品。\n3. 舉辦集會。\n4. 把資料列入教材。\n5. 利用網際網路。",
        "explanation": "職安法第 26 條。",
        "mnemonic": "口訣：公印集教網",
        "hint": "思考一下：在學校或公司，老闆都怎麼傳達消息給你的？(貼在牆上？發傳單？開會？)",
        "keywords": ["公告", "印刷品", "集會", "教材", "網路", "網際網路"]
    },
    {
        "id": 302,
        "category": "營造與高處",
        "question": "依職業安全衛生設施規則規定，使用「合梯」進行作業時，應符合哪些規定？(請列舉 4 項)",
        "answer": "1. 具有堅固之構造。\n2. 材質不得有顯著之損傷、腐蝕等。\n3. 梯腳與地面之角度應在 75 度以內。\n4. 兩梯腳間有金屬繫材扣牢。",
        "explanation": "合梯作業必考題。",
        "mnemonic": "口訣：固損七五繫",
        "hint": "想一下梯子的結構：材質要怎樣？角度要多斜？兩隻腳中間要有什麼才不會劈腿？",
        "keywords": ["堅固", "損傷", "75度", "75 度", "繫材", "扣牢"]
    },
    {
        "id": 303,
        "category": "法規與管理",
        "question": "依職業安全衛生法規定，發生職業災害時，雇主應採取的 3 大步驟為何？",
        "answer": "1. 採取必要之急救、搶救等措施。\n2. 實施調查、分析及作成紀錄。\n3. 於 8 小時內通報勞動檢查機構。",
        "explanation": "職災通報 S.O.P.",
        "mnemonic": "口訣：救查報",
        "hint": "事情發生了，第一步先救人，第二步查原因，第三步要跟誰報告？",
        "keywords": ["急救", "搶救", "調查", "紀錄", "通報", "8小時", "8 小時"]
    },
    {
        "id": 304,
        "category": "電氣與機械",
        "question": "依職業安全衛生法規定，請列舉 5 種具有危險性之機械？",
        "answer": "1. 固定式起重機。\n2. 移動式起重機。\n3. 人字臂起重桿。\n4. 營建用升降機。\n5. 吊籠。",
        "explanation": "危險性機械清單。",
        "mnemonic": "口訣：吊人移固升",
        "hint": "想像工地上那些會把東西吊起來、升上去的大型機器。",
        "keywords": ["固定式", "移動式", "起重機", "人字臂", "升降機", "吊籠"]
    },
    {
        "id": 305,
        "category": "化學與缺氧",
        "question": "進入局限空間（缺氧危險作業）前，應採取哪些措施？(列舉 4 項)",
        "answer": "1. 實施通風換氣。\n2. 測定氧氣及危害氣體濃度。\n3. 置備救援設備。\n4. 派人監視。",
        "explanation": "缺氧作業 SOP。",
        "mnemonic": "口訣：風測救監",
        "hint": "進去下水道前，怕沒空氣要先做什麼？萬一暈倒了外面要有人做什麼？",
        "keywords": ["通風", "換氣", "測定", "濃度", "救援", "監視"]
    }
]

def add_subjective_questions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    print(f"🚀 正在注入 {len(subjective_data)} 題含 AI 引導的術科題...")
    
    for q in subjective_data:
        c.execute("DELETE FROM questions WHERE id = ?", (q['id'],))
        
        options_str = json.dumps([], ensure_ascii=False)
        keywords_str = json.dumps(q["keywords"], ensure_ascii=False)
        
        c.execute('''
            INSERT INTO questions (id, category, type, question, options, answer, explanation, mnemonic, keywords, hint)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            q["id"], q["category"], "essay", q["question"], options_str, q["answer"], q["explanation"], q["mnemonic"], keywords_str, q["hint"]
        ))
    conn.commit()
    conn.close()
    print("🎉 術科特訓題庫注入完成！")

if __name__ == "__main__":
    add_subjective_questions()