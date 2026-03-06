import sqlite3
import streamlit as st

DB_PATH = "course2.db"

@st.cache_data
def get_teacher_options():
    """从数据库提取教师名单，返回包含 ID 和显示标签的字典列表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. 检查 teachers 表是否存在
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='teachers'")
        if cursor.fetchone()[0] == 0:
            return []
            
        # 2. 严格按照你的数据库字段查询：teacher_id, name, department
        query = "SELECT teacher_id, name, department FROM teachers ORDER BY department, name"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        # 3. 构造字典：label 决定了用户看到的内容，我们这里只放“姓名 (学院)”
        return [{"teacher_id": r[0], "label": f"{r[1]} ({r[2]})"} for r in results]
    except Exception as e:
        print(f"Error loading teachers: {e}")
        return []

def save_survey_to_db(data_dict):
    """将问卷数据写入数据库，使用 teacher_id 作为外键"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. 如果评价表不存在，则创建 (修正列名为 teacher_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER,
                attendance_freq TEXT,
                attendance_method TEXT,
                roll_call TEXT,
                roll_call_logic TEXT,
                interaction_style TEXT,
                exam_tips TEXT,
                grading_style TEXT,
                workload TEXT,
                special_notes TEXT,
                timestamp REAL,
                FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id)
            )
        ''')
        
        # 2. 插入数据 (确保字段与数据字典 key 一一对应)
        query = '''
            INSERT INTO evaluations 
            (teacher_id, attendance_freq, attendance_method, roll_call, roll_call_logic, 
             interaction_style, exam_tips, grading_style, workload, special_notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (
            data_dict["teacher_id"],
            data_dict["attendance_freq"],
            data_dict["attendance_method"],
            data_dict["roll_call"],
            data_dict["roll_call_logic"],
            data_dict["interaction_style"],
            data_dict["exam_tips"],
            data_dict["grading_style"],
            data_dict["workload"],
            data_dict["special_notes"],
            data_dict["timestamp"]
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        # 在后台打印具体报错，方便调试
        print(f"Database Save Error: {e}")
        return False
    
def get_collection_progress():
    """
    计算进度：统计 evaluations 表中不重复的 teacher_id 数量
    """
    # 请确保 DB_PATH 指向你正确的 SQLite 数据库文件
    conn = sqlite3.connect('course2.db') 
    cursor = conn.cursor()
    
    # 统计至少有一条评价的老师数量
    cursor.execute("SELECT COUNT(DISTINCT teacher_id) FROM evaluations")
    covered_count = cursor.fetchone()[0]
    
    # 统计清洗后的总老师人数
    cursor.execute("SELECT COUNT(*) FROM teachers")
    total_count = cursor.fetchone()[0]
    
    conn.close()
    return covered_count, total_count