import json
import sqlite3

def init_database(json_path, db_path="course2.db"):
    # 1. 加载 JSON 数据
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    teachers_data = data.get('teachers', []) # 

    # 2. 连接数据库（如果不存在则创建）
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 3. 创建教师名单表 (静态)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    ''')

    # 4. 创建评价记录表 (动态，对应你设计的10个问题)
    # 使用 teacher_id 作为外键关联，支持一个老师拥有多条评价
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT,
            attendance_freq TEXT,
            attendance_method TEXT,
            rollcall TEXT,
            rollcall_logic TEXT,
            interaction_style TEXT,
            exam_tips TEXT,
            grading_style TEXT,
            workload TEXT,
            special_notes TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id)
        )
    ''')

    # 5. 批量导入教师名单 
    # 我们只取教师号、姓名、学院名
    teacher_tuples = [
        (t['teacherNumber'], t['teacherName'], t['departmentName']) 
        for t in teachers_data
    ]

    cursor.executemany(
        "INSERT OR REPLACE INTO teachers (teacher_id, name, department) VALUES (?, ?, ?)",
        teacher_tuples
    )

    conn.commit()
    conn.close()
    print(f"✅ 成功导入 {len(teacher_tuples)} 名教师数据到 {db_path}")

if __name__ == "__main__":
    init_database("teacher_list.json")